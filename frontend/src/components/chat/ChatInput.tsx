"use client";

import React, { useState, useRef, useEffect } from "react";
import { useLanguage } from "@/context/LanguageContext";

/**
 * ChatInput component.
 * 
 * Handles user message input with auto-expanding textarea, send button,
 * and voice input using browser-native Speech Recognition.
 */

interface ChatInputProps {
    onSendMessage: (message: string) => void;
    isLoading: boolean;
}

// Global type for SpeechRecognition to avoid TS errors
declare global {
    interface Window {
        SpeechRecognition: any;
        webkitSpeechRecognition: any;
    }
}

/** Fix common voice mishearings for todo/task commands */
function cleanVoiceTranscript(text: string): string {
    if (!text?.trim()) return text;
    let t = text
        .replace(/\b(to do|to-do)\b/gi, "todo")
        .replace(/\b(ad|at)\s+urgent\b/gi, "add urgent")
        .replace(/\b(over do|over due|over you|about you|overdo)\b/gi, "overdue")
        .replace(/\b(due to day|do today)\b/gi, "due today")
        .replace(/\b(show me)\s+(my\s+)?tasks?\b/gi, "show my tasks")
        .replace(/\s+/g, " ")
        .trim();

    // "show overdue tasks" — many ways speech recognition mishears "overdue"
    const overduePatterns = [
        /\bshow\s+(about\s+you|about\s+your|over\s+you|over\s+your|of\s+you|a\s+bout\s+you)\s+task(s?)\b/gi,
        /\bshow\s+about\s+you\s+task(s?)\b/gi,
        /\bshow\s+over\s+you\s+task(s?)\b/gi,
        /\b(about\s+you|over\s+you)\s+task(s?)\b/gi,
        /\bshow\s+about\s+you\b/gi,
        /\bshow\s+overdue\s+task\b/gi,  // "show overdue task" -> "show overdue tasks"
    ];
    for (const p of overduePatterns) {
        t = t.replace(p, "show overdue tasks");
    }

    // "show my task" -> "show my tasks"
    t = t.replace(/\bshow\s+my\s+task\b/gi, "show my tasks");

    // "add a task" / "add task" variations
    t = t.replace(/\badd\s+a\s+task\s+to\s+/gi, "add task ");
    t = t.replace(/\badd\s+urgent\s+task\s+to\s+/gi, "add urgent task ");

    return t;
}

export default function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
    const { language, t } = useLanguage();
    const [message, setMessage] = useState("");
    const [isListening, setIsListening] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const recognitionRef = useRef<any>(null);

    const handleSubmit = (e?: React.FormEvent) => {
        e?.preventDefault();
        if (message.trim() && !isLoading) {
            onSendMessage(message.trim());
            setMessage("");
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    // Initialize Speech Recognition
    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            try {
                recognitionRef.current = new SpeechRecognition();
                recognitionRef.current.continuous = false;
                recognitionRef.current.interimResults = false;

                recognitionRef.current.onresult = (event: any) => {
                    try {
                        const transcript = event.results[0][0].transcript;
                        if (transcript) {
                            const cleaned = cleanVoiceTranscript(transcript);
                            setMessage((prev) => (prev ? `${prev} ${cleaned}` : cleaned));
                        }
                    } catch (e) {
                        console.error("Speech result parsing error:", e);
                    }
                    setIsListening(false);
                };

                recognitionRef.current.onerror = (event: any) => {
                    if (event.error !== "aborted" && event.error !== "no-speech") {
                        console.error("Speech recognition error:", event.error);
                    }
                    setIsListening(false);
                };

                recognitionRef.current.onend = () => {
                    setIsListening(false);
                };
            } catch (e) {
                console.error("Speech recognition init error:", e);
                recognitionRef.current = null;
            }
        }

        return () => {
            try {
                if (recognitionRef.current) {
                    recognitionRef.current.stop?.();
                }
            } catch (_) { /* ignore */ }
        };
    }, []);

    const toggleListening = () => {
        if (!recognitionRef.current) {
            alert("Speech recognition is not supported in this browser. Try Chrome.");
            return;
        }

        if (isListening) {
            try {
                recognitionRef.current.stop();
            } catch (_) { /* ignore */ }
            setIsListening(false);
        } else {
            try {
                recognitionRef.current.lang = language === "ur" ? "ur-PK" : "en-US";
                recognitionRef.current.start();
                setIsListening(true);
            } catch (e) {
                console.error("Speech start error:", e);
                alert("Could not start microphone. Check permissions and try Chrome.");
            }
        }
    };

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    }, [message]);

    const quickCommands = language === "ur"
        ? [
            { label: "فہرست دکھائیں", cmd: "میرے ٹاسک دکھائیں" },
            { label: "فوری ٹاسک", cmd: "فوری ٹاسک شامل کریں " },
            { label: "مدت ختم", cmd: "مدت ختم شدہ ٹاسک دکھائیں" },
            { label: "تلاش", cmd: "ٹاسک تلاش کریں " },
        ]
        : [
            { label: "My Tasks", cmd: "Show my tasks" },
            { label: "Add Urgent", cmd: "Add urgent task " },
            { label: "Overdue", cmd: "Show overdue tasks" },
            { label: "Search", cmd: "Search tasks " },
            { label: "Due Today", cmd: "Show tasks due today" },
            { label: "#tagged", cmd: "Find tasks tagged #" },
        ];

    const handleQuickCommand = (cmd: string) => {
        if (cmd.endsWith(" ") || cmd.endsWith("#")) {
            setMessage(cmd);
            textareaRef.current?.focus();
        } else {
            onSendMessage(cmd);
        }
    };

    return (
        <div className="p-4 bg-white border-t border-gray-200">
            <div className="max-w-4xl mx-auto mb-2 flex items-center gap-2 overflow-x-auto scrollbar-hide">
                {quickCommands.map((qc) => (
                    <button
                        key={qc.label}
                        type="button"
                        onClick={() => handleQuickCommand(qc.cmd)}
                        disabled={isLoading}
                        className="flex-shrink-0 px-3 py-1 text-xs font-medium rounded-full border border-gray-200 bg-gray-50 text-gray-600 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200 transition-colors disabled:opacity-50"
                    >
                        {qc.label}
                    </button>
                ))}
                <span className="flex-shrink-0 text-xs px-2 py-1 rounded bg-gray-100 text-gray-500">
                    🎤 {language === "ur" ? t("chat.voice.ur") : t("chat.voice.en")}
                </span>
            </div>
            <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto flex items-end space-x-2">
                <div className="flex-1 relative">
                    <textarea
                        ref={textareaRef}
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={isListening ? t("chat.listening") : t("chat.input.placeholder")}
                        className={`w-full p-3 pr-12 text-sm text-gray-900 bg-gray-50 rounded-2xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none overflow-y-auto transition-all duration-200 ease-in-out scrollbar-hide min-h-[44px] max-h-[200px] ${isListening ? "ring-2 ring-red-400 border-transparent animate-pulse" : ""
                            }`}
                        rows={1}
                        disabled={isLoading}
                    />
                </div>

                <button
                    type="button"
                    onClick={toggleListening}
                    disabled={isLoading}
                    className={`p-3 rounded-xl transition-all duration-200 shadow-sm ${isListening
                        ? "bg-red-500 text-white animate-pulse"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                        }`}
                    title={isListening ? "Stop listening" : "Voice input — Try: Show my tasks, Add task buy milk, Show overdue tasks"}
                >
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m8 0h-4m-4-8a3 3 0 013-3V5a3 3 0 116 0v6a3 3 0 01-3 3 3 3 0 01-3-3z"></path>
                    </svg>
                </button>

                <button
                    type="submit"
                    disabled={!message.trim() || isLoading}
                    className={`p-3 rounded-xl transition-all duration-200 shadow-sm ${!message.trim() || isLoading
                        ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                        : "bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-md active:scale-95"
                        }`}
                >
                    {isLoading ? (
                        <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    ) : (
                        <svg className="h-5 w-5 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                        </svg>
                    )}
                </button>
            </form>
        </div>
    );
}

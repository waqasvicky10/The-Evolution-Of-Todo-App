"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

type Language = "en" | "ur";

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const translations = {
    en: {
        "nav.home": "Home",
        "nav.dashboard": "Dashboard",
        "nav.chat": "AI Chat",
        "nav.login": "Login",
        "nav.register": "Register",
        "nav.logout": "Logout",
        "chat.input.placeholder": "Type or speak your message...",
        "chat.listening": "Listening...",
        "chat.voice.en": "English (US)",
        "chat.voice.ur": "Urdu (PK)",
        "landing.title": "Todo App",
        "landing.subtitle": "Phase V - Event-Driven Architecture",
        "landing.description": "An event-driven todo app with Dapr, Redpanda, advanced task management, and AI chatbot.",
        "landing.secure": "Secure",
        "landing.persistent": "Persistent",
        "landing.multiuser": "Multi-User",
        "landing.getstarted": "Get Started",
        "landing.signin": "Sign In",
        "dashboard.title": "My Tasks",
        "dashboard.search": "Search tasks...",
        "dashboard.filter.all": "All",
        "dashboard.filter.active": "Active",
        "dashboard.filter.completed": "Completed",
        "dashboard.sort.newest": "Newest First",
        "dashboard.sort.oldest": "Oldest First",
        "dashboard.sort.dueDate": "Due Date",
        "dashboard.sort.priority": "Priority",
        "dashboard.priority.urgent": "Urgent",
        "dashboard.priority.high": "High",
        "dashboard.priority.medium": "Medium",
        "dashboard.priority.low": "Low",
        "dashboard.overdue": "Overdue",
        "dashboard.noTasks": "No tasks yet",
        "dashboard.createFirst": "Create your first task to get started!",
        "task.dueDate": "Due",
        "task.recurring": "Recurring",
        "task.tags": "Tags",
    },
    ur: {
        "nav.home": "ہوم",
        "nav.dashboard": "ڈیش بورڈ",
        "nav.chat": "AI چیٹ",
        "nav.login": "لاگ ان",
        "nav.register": "رجسٹر",
        "nav.logout": "لاگ آؤٹ",
        "chat.input.placeholder": "اپنا پیغام لکھیں یا بولیں...",
        "chat.listening": "سن رہا ہے...",
        "chat.voice.en": "انگریزی (US)",
        "chat.voice.ur": "اردو (PK)",
        "landing.title": "ٹو ڈو ایپ",
        "landing.subtitle": "فیز V - ایونٹ سے چلنے والا فن تعمیر",
        "landing.description": "Dapr، Redpanda، جدید ٹاسک مینجمنٹ، اور AI چیٹ بوٹ کے ساتھ ایونٹ سے چلنے والی ٹو ڈو ایپ۔",
        "landing.secure": "محفوظ",
        "landing.persistent": "مستقل",
        "landing.multiuser": "ملٹی یوزر",
        "landing.getstarted": "شروع کریں",
        "landing.signin": "سائن ان",
        "dashboard.title": "میری ٹاسکس",
        "dashboard.search": "ٹاسکس تلاش کریں...",
        "dashboard.filter.all": "سب",
        "dashboard.filter.active": "فعال",
        "dashboard.filter.completed": "مکمل",
        "dashboard.sort.newest": "نئے پہلے",
        "dashboard.sort.oldest": "پرانے پہلے",
        "dashboard.sort.dueDate": "آخری تاریخ",
        "dashboard.sort.priority": "ترجیح",
        "dashboard.priority.urgent": "فوری",
        "dashboard.priority.high": "اعلیٰ",
        "dashboard.priority.medium": "درمیانی",
        "dashboard.priority.low": "کم",
        "dashboard.overdue": "مدت ختم",
        "dashboard.noTasks": "ابھی کوئی ٹاسک نہیں",
        "dashboard.createFirst": "شروع کرنے کے لیے اپنا پہلا ٹاسک بنائیں!",
        "task.dueDate": "آخری تاریخ",
        "task.recurring": "بار بار",
        "task.tags": "ٹیگز",
    }
};

export function LanguageProvider({ children }: { children: React.ReactNode }) {
    const [language, setLanguage] = useState<Language>("en");

    // Load saved language from localStorage
    useEffect(() => {
        const savedLang = localStorage.getItem("language") as Language;
        if (savedLang && (savedLang === "en" || savedLang === "ur")) {
            setLanguage(savedLang);
        }
    }, []);

    const handleSetLanguage = (lang: Language) => {
        setLanguage(lang);
        localStorage.setItem("language", lang);
    };

    const t = (key: string) => {
        return translations[language][key as keyof typeof translations["en"]] || key;
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage: handleSetLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error("useLanguage must be used within a LanguageProvider");
    }
    return context;
}

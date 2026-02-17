/**
 * Todo Chat UI - JavaScript
 *
 * This file handles:
 * - Authentication
 * - Message sending/receiving
 * - Conversation history loading
 * - UI updates and interactions
 */

// Configuration
// Use localhost API for local dev, production backend URL for deployed environments
const API_BASE_URL = (window.location.protocol === 'file:' ||
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    !window.location.hostname)
    ? 'http://localhost:8000/api'
    : 'https://the-evolution-of-todo-app-phase-iv-api.vercel.app/api';

// Log API URL for debugging
console.log('API Base URL:', API_BASE_URL);
console.log('Current location:', window.location.href);
console.log('Protocol:', window.location.protocol);

const AUTH_TOKEN_KEY = 'todo_chat_token';
const USER_NAME_KEY = 'todo_chat_user';

// State
let authToken = null;
let isProcessing = false;

// DOM Elements
const loginScreen = document.getElementById('login-screen');
const chatContainer = document.getElementById('chat-container');
const loginForm = document.getElementById('login-form');
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const voiceButton = document.getElementById('voice-button');
const messagesContainer = document.getElementById('messages-container');
const userNameDisplay = document.getElementById('user-name');
const logoutBtn = document.getElementById('logout-btn');
const statusText = document.getElementById('status-text');
const sendIcon = document.getElementById('send-icon');
const loadingSpinner = document.getElementById('loading-spinner');

// Voice Recognition
let recognition = null;
let isRecording = false;
// Track permission state - check localStorage first for persistence
let microphonePermissionGranted = localStorage.getItem('microphone_permission_granted') === 'true';

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    checkAuthentication();
    setupEventListeners();
    setupLanguageMenu();

    // Check microphone permission state (don't request if already granted)
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
            // Try to use Permissions API first (if available)
            if (navigator.permissions && navigator.permissions.query) {
                try {
                    const permissionStatus = await navigator.permissions.query({ name: 'microphone' });
                    console.log('Microphone permission state:', permissionStatus.state);

                    if (permissionStatus.state === 'granted') {
                        microphonePermissionGranted = true;
                        localStorage.setItem('microphone_permission_granted', 'true');
                        console.log('Microphone permission already granted');
                    } else if (permissionStatus.state === 'prompt' && !microphonePermissionGranted) {
                        // Only request if in 'prompt' state (not yet asked) AND not already granted
                        try {
                            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                            stream.getTracks().forEach(track => track.stop());
                            microphonePermissionGranted = true;
                            localStorage.setItem('microphone_permission_granted', 'true');
                            console.log('Microphone permission granted on page load');
                        } catch (error) {
                            console.log('Microphone permission denied:', error.name);
                            localStorage.setItem('microphone_permission_granted', 'false');
                        }
                    } else {
                        console.log('Microphone permission denied, user needs to enable in browser settings');
                        localStorage.setItem('microphone_permission_granted', 'false');
                    }

                    // Listen for permission changes
                    permissionStatus.onchange = () => {
                        microphonePermissionGranted = permissionStatus.state === 'granted';
                        console.log('Microphone permission state changed to:', permissionStatus.state);
                    };
                } catch (permError) {
                    // Permissions API might not support 'microphone' name, use fallback
                    console.log('Permissions API error, using fallback:', permError);
                    // Fall through to fallback
                }
            }

            // Fallback: Check permission by trying to access (only if not already granted)
            if (!microphonePermissionGranted) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    stream.getTracks().forEach(track => track.stop());
                    microphonePermissionGranted = true;
                    localStorage.setItem('microphone_permission_granted', 'true');
                    console.log('Microphone permission granted (fallback)');
                } catch (err) {
                    console.log('Microphone permission not granted (will request when needed):', err.name);
                    localStorage.setItem('microphone_permission_granted', 'false');
                }
            }
        } catch (error) {
            console.log('Error checking microphone permission:', error);
        }
    }
});

/**
 * Setup language menu logic
 */
function setupLanguageMenu() {
    const langBtn = document.getElementById('lang-btn');
    const langMenu = document.getElementById('lang-menu');
    const langOptions = document.querySelectorAll('.lang-option');
    const currentLangIcon = document.getElementById('current-lang-icon');

    // Load stored language
    const storedLang = localStorage.getItem('todo_chat_lang') || 'en';
    updateLanguageUI(storedLang);

    // Toggle menu
    langBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        langMenu.classList.toggle('show');
    });

    // Handle option click
    langOptions.forEach(option => {
        option.addEventListener('click', (e) => {
            const selectedLang = e.currentTarget.dataset.lang;
            localStorage.setItem('todo_chat_lang', selectedLang);

            updateLanguageUI(selectedLang);

            // Update recognition if active
            if (recognition) {
                recognition.lang = selectedLang === 'ur' ? 'ur-PK' : 'en-US';
            }

            langMenu.classList.remove('show');
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!langMenu.contains(e.target) && !langBtn.contains(e.target)) {
            langMenu.classList.remove('show');
        }
    });

    function updateLanguageUI(lang) {
        // Update icon
        currentLangIcon.textContent = lang === 'ur' ? '🇵🇰' : '🇺🇸';

        // Update active class
        langOptions.forEach(opt => {
            if (opt.dataset.lang === lang) {
                opt.classList.add('active');
            } else {
                opt.classList.remove('active');
            }
        });
    }
}

/**
 * Check if user is already authenticated
 */
function checkAuthentication() {
    const savedToken = localStorage.getItem(AUTH_TOKEN_KEY);
    const savedUsername = localStorage.getItem(USER_NAME_KEY);

    if (savedToken && savedUsername) {
        authToken = savedToken;
        login(savedUsername);
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Login form
    loginForm.addEventListener('submit', handleLogin);

    // Message form
    messageForm.addEventListener('submit', handleSendMessage);

    // Logout button
    logoutBtn.addEventListener('click', handleLogout);

    // Voice button
    if (voiceButton) {
        voiceButton.addEventListener('click', handleVoiceInput);
    }

    // Enter key in message input
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage(e);
        }
    });

    // Voice recognition will be initialized after permission check in DOMContentLoaded
}

/**
 * Handle login form submission
 */
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showError('Please enter username and password');
        return;
    }

    // For demo purposes, we'll use a test token
    // In production, this would call an authentication endpoint
    authToken = 'test_token';
    localStorage.setItem(AUTH_TOKEN_KEY, authToken);
    localStorage.setItem(USER_NAME_KEY, username);

    login(username);
}

/**
 * Perform login (show chat, load history)
 */
async function login(username) {
    // Update UI
    loginScreen.style.display = 'none';
    chatContainer.style.display = 'flex';
    userNameDisplay.textContent = username;
    messageInput.disabled = false;
    sendButton.disabled = false;
    enableVoiceButton();

    // Load conversation history
    await loadConversationHistory();

    // Focus message input
    messageInput.focus();

    setStatus('Ready');
}

/**
 * Handle logout
 */
function handleLogout() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(USER_NAME_KEY);
    authToken = null;

    // Clear messages
    const messages = messagesContainer.querySelectorAll('.message');
    messages.forEach(msg => msg.remove());

    // Show login screen
    chatContainer.style.display = 'none';
    loginScreen.style.display = 'flex';

    // Reset form
    loginForm.reset();
}

/**
 * Load conversation history from API
 */
async function loadConversationHistory() {
    try {
        setStatus('Loading history...');

        const response = await fetch(`${API_BASE_URL}/chat/history?limit=50`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load history');
        }

        const data = await response.json();

        // Display messages
        if (data.messages && data.messages.length > 0) {
            // Remove welcome message
            const welcomeMsg = messagesContainer.querySelector('.welcome-message');
            if (welcomeMsg) {
                welcomeMsg.remove();
            }

            data.messages.forEach(msg => {
                appendMessage(msg.role, msg.content, msg.timestamp, false);
            });

            scrollToBottom();
        }

        setStatus('Ready');
    } catch (error) {
        console.error('Error loading history:', error);
        setStatus('Error loading history');
    }
}

/**
 * Handle send message
 */
async function handleSendMessage(e) {
    e.preventDefault();

    const message = messageInput.value.trim();

    if (!message || isProcessing) {
        return;
    }

    // Disable input while processing
    isProcessing = true;
    messageInput.disabled = true;
    sendButton.disabled = true;
    showLoading(true);
    setStatus('Sending...');

    try {
        // Display user message immediately
        const timestamp = new Date().toISOString();
        appendMessage('user', message, timestamp);
        messageInput.value = '';
        scrollToBottom();

        // Send to API
        setStatus('AI is thinking...');
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            if (response.status === 401) {
                handleLogout();
                showError('Session expired. Please log in again.');
                return;
            }
            throw new Error('Failed to send message');
        }

        const data = await response.json();

        // Log response for debugging
        console.log('API Response:', data);
        if (data && data.response) {
            console.log('Bot says:', data.response);
        }

        // Ensure we have a response
        if (!data || !data.response || (typeof data.response === 'string' && data.response.trim() === '')) {
            console.warn('Empty or invalid response from API:', data);
            data.response = data.response || 'I received your message but got an empty response. Please try again.';
        }

        // Display assistant response - ensure response is always a string
        const responseText = String(data.response || 'No response received');
        appendMessage('assistant', responseText, data.timestamp || new Date().toISOString(), true, data.tool_calls || []);
        scrollToBottom();

        setStatus('Ready');
    } catch (error) {
        console.error('Error sending message:', error);
        showError('Failed to send message. Please try again.');
        setStatus('Error');
    } finally {
        // Re-enable input
        isProcessing = false;
        messageInput.disabled = false;
        sendButton.disabled = false;
        showLoading(false);
        messageInput.focus();
    }
}

/**
 * Append a message to the chat
 */
function appendMessage(role, content, timestamp, animate = true, toolCalls = []) {
    // Remove welcome message if it exists
    const welcomeMsg = messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    // Use innerHTML to preserve formatting and support Urdu text
    // Ensure content is a string and handle null/undefined
    const safeContent = String(content || 'No response received');
    bubble.innerHTML = safeContent.replace(/\n/g, '<br>');

    const timestampDiv = document.createElement('div');
    timestampDiv.className = 'message-timestamp';
    timestampDiv.textContent = formatTimestamp(timestamp);

    contentDiv.appendChild(bubble);
    contentDiv.appendChild(timestampDiv);

    // Add tool call indicators if present
    if (toolCalls && toolCalls.length > 0) {
        const toolCallsDiv = document.createElement('div');
        toolCallsDiv.className = 'tool-calls';
        toolCallsDiv.innerHTML = '<strong>🛠️ Actions:</strong>';

        toolCalls.forEach(tc => {
            const toolItem = document.createElement('div');
            toolItem.className = 'tool-call-item';
            toolItem.textContent = `✓ ${tc.tool_name}`;
            toolCallsDiv.appendChild(toolItem);
        });

        contentDiv.appendChild(toolCallsDiv);
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    messagesContainer.appendChild(messageDiv);

    if (animate) {
        setTimeout(() => scrollToBottom(), 100);
    }
}

/**
 * Format timestamp for display
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();

    const isToday = date.toDateString() === now.toDateString();

    if (isToday) {
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    } else {
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit'
        });
    }
}

/**
 * Scroll to bottom of messages
 */
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Show/hide loading spinner
 */
function showLoading(show) {
    sendIcon.style.display = show ? 'none' : 'inline';
    loadingSpinner.style.display = show ? 'inline' : 'none';
}

/**
 * Set status text
 */
function setStatus(text) {
    statusText.textContent = text;
}

/**
 * Show error message
 */
function showError(message) {
    const errorToast = document.getElementById('error-toast');
    const errorMessage = document.getElementById('error-message');

    errorMessage.textContent = message;
    errorToast.style.display = 'flex';

    setTimeout(() => {
        hideError();
    }, 5000);
}

/**
 * Hide error message
 */
function hideError() {
    const errorToast = document.getElementById('error-toast');
    errorToast.style.display = 'none';
}

/**
 * Correct common speech recognition errors
 */
function correctSpeechRecognitionErrors(text) {
    if (!text) return text;

    // Common misrecognitions: "86" -> "6", "80" -> "8", etc.
    // Fix numbers that are likely misrecognitions (when followed by task/ID context)
    // Fix "ID 86" -> "ID 6" specifically (most common issue)
    text = text.replace(/\bid\s+86\b/gi, 'id 6');
    text = text.replace(/\btask\s+86\b/gi, 'task 6');
    text = text.replace(/\bnumber\s+86\b/gi, 'number 6');
    text = text.replace(/\b86\s+task\b/gi, '6 task');
    text = text.replace(/\b86\s+completed\b/gi, '6 completed');
    text = text.replace(/\b86\s+is\s+completed\b/gi, '6 is completed');

    // Fix other common number misrecognitions in task context
    text = text.replace(/\bid\s+80\b/gi, 'id 8');
    text = text.replace(/\bid\s+87\b/gi, 'id 7');
    text = text.replace(/\bid\s+85\b/gi, 'id 5');
    text = text.replace(/\bid\s+84\b/gi, 'id 4');
    text = text.replace(/\bid\s+83\b/gi, 'id 3');
    text = text.replace(/\bid\s+82\b/gi, 'id 2');
    text = text.replace(/\bid\s+81\b/gi, 'id 1');
    text = text.replace(/\bid\s+90\b/gi, 'id 9');

    // Fix standalone number misrecognitions (less aggressive)
    text = text.replace(/\b86\b(?=\s*(?:task|completed|done|finished|is|was))/gi, '6');
    text = text.replace(/\b80\b(?=\s*(?:task|completed|done|finished|is|was))/gi, '8');

    // Fix common word misrecognitions
    text = text.replace(/\bto do\b/gi, 'todo');
    text = text.replace(/\bto-do\b/gi, 'todo');
    text = text.replace(/\btwo do\b/gi, 'todo');

    return text;
}

/**
 * Request microphone permission upfront
 */
async function requestMicrophonePermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Permission granted, stop the stream immediately
        stream.getTracks().forEach(track => track.stop());
        console.log('Microphone permission granted');
        return true;
    } catch (error) {
        console.warn('Microphone permission denied or not available:', error);
        return false;
    }
}

/**
 * Initialize voice recognition
 * NOTE: This should be called AFTER microphone permission is granted
 */
function initVoiceRecognition() {
    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn('Speech recognition not supported in this browser');
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    // IMPORTANT: Set serviceURI to prevent permission prompts if possible
    // Some browsers require this to be set before using recognition

    // Default to stored language or English
    const storedLang = localStorage.getItem('todo_chat_lang') || 'en';
    recognition.lang = storedLang === 'ur' ? 'ur-PK' : 'en-US';

    recognition.onstart = () => {
        isRecording = true;
        voiceButton.classList.add('recording');
        setStatus('🎤 Listening...');
    };

    recognition.onresult = (event) => {
        const originalTranscript = event.results[0][0].transcript;
        let transcript = originalTranscript;

        // Correct common speech recognition errors
        transcript = correctSpeechRecognitionErrors(transcript);

        console.log('Original transcript:', originalTranscript);
        console.log('Corrected transcript:', transcript);

        messageInput.value = transcript;
        setStatus('Processing voice input...');

        // Automatically send the message
        setTimeout(() => {
            if (messageInput.value.trim()) {
                handleSendMessage(new Event('submit'));
            }
        }, 500);
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        isRecording = false;
        voiceButton.classList.remove('recording');

        let errorMsg = 'Voice input failed';
        if (event.error === 'no-speech') {
            errorMsg = 'No speech detected. Please try again.';
        } else if (event.error === 'not-allowed') {
            errorMsg = 'Microphone access denied. Please enable it in your browser settings.';
        }

        showError(errorMsg);
        setStatus('Ready');
    };

    recognition.onend = () => {
        isRecording = false;
        voiceButton.classList.remove('recording');
        if (statusText.textContent === '🎤 Listening...') {
            setStatus('Ready');
        }
    };
}

/**
 * Handle voice input button click
 */
async function handleVoiceInput() {
    if (isRecording) {
        // Stop recording
        if (recognition) {
            recognition.stop();
        }
        return;
    }

    // CRITICAL FIX: Check actual permission state using Permissions API
    // This prevents repeated prompts by checking browser's actual permission state
    let shouldRequestPermission = true;

    if (navigator.permissions && navigator.permissions.query) {
        try {
            const permissionStatus = await navigator.permissions.query({ name: 'microphone' });
            console.log('Microphone permission state:', permissionStatus.state);

            if (permissionStatus.state === 'granted') {
                microphonePermissionGranted = true;
                localStorage.setItem('microphone_permission_granted', 'true');
                shouldRequestPermission = false;
                console.log('✅ Permission already granted (from Permissions API)');
            } else if (permissionStatus.state === 'denied') {
                microphonePermissionGranted = false;
                localStorage.setItem('microphone_permission_granted', 'false');
                shouldRequestPermission = false;
                showError('Microphone permission denied. Please enable it in browser settings.');
                return;
            }
            // If 'prompt', we'll request permission below
        } catch (permError) {
            console.log('Permissions API not available, using fallback:', permError);
            // Fall through to getUserMedia check
        }
    }

    // Request permission via getUserMedia if needed
    if (shouldRequestPermission && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // Only request if not already granted (check localStorage as backup)
        if (!microphonePermissionGranted) {
            try {
                console.log('Requesting microphone permission before starting recognition...');
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                stream.getTracks().forEach(track => track.stop());
                microphonePermissionGranted = true;
                localStorage.setItem('microphone_permission_granted', 'true');
                console.log('✅ Microphone permission granted - recognition can start without prompt');
            } catch (error) {
                if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                    microphonePermissionGranted = false;
                    localStorage.setItem('microphone_permission_granted', 'false');
                    showError('Microphone permission denied. Please allow microphone access in your browser settings.');
                    return;
                }
                console.warn('Microphone permission check failed:', error);
                // Continue anyway - might work if permission was granted previously
            }
        } else {
            console.log('✅ Microphone permission already granted (from localStorage) - starting recognition');
        }
    }

    // Check if recognition is available
    if (!recognition) {
        initVoiceRecognition();
        if (!recognition) {
            showError('Voice input not available in this browser');
            return;
        }
    }

    // Use stored language preference
    const storedLang = localStorage.getItem('todo_chat_lang') || 'en';
    recognition.lang = storedLang === 'ur' ? 'ur-PK' : 'en-US';

    // Start recording - permission should already be granted at this point
    try {
        console.log('Starting SpeechRecognition (permission should be granted)...');
        recognition.start();
    } catch (error) {
        console.error('Error starting recognition:', error);
        isRecording = false;
        voiceButton.classList.remove('recording');

        if (error.name === 'InvalidStateError') {
            showError('Voice recognition is already running');
        } else if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            // Permission was denied - update state
            microphonePermissionGranted = false;
            localStorage.setItem('microphone_permission_granted', 'false');
            showError('Microphone permission denied. Please allow microphone access in your browser settings.');
            setStatus('Permission denied');
        } else {
            showError('Failed to start voice recognition. Please try again.');
            setStatus('Error');
        }
    }
}

/**
 * Enable voice button after login
 */
function enableVoiceButton() {
    if (voiceButton) {
        voiceButton.disabled = false;

        // Visual indicator if not supported
        if (!recognition) {
            voiceButton.classList.add('disabled-look');
        }
    }
}

/**
 * Set input text
 */
function setInput(text) {
    messageInput.value = text;
    messageInput.focus();
}

/**
 * Send a message programmatically
 */
function sendMessage(text) {
    messageInput.value = text;
    handleSendMessage(new Event('submit'));
}

// Export for inline onclick handler
window.hideError = hideError;
window.setInput = setInput;
window.sendMessage = sendMessage;

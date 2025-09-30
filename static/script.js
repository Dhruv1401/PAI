const socket = io('http://localhost:5001');
const messages = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const micButton = document.getElementById('micButton');
const logOutput = document.getElementById('logOutput');

// Send message
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

function sendMessage() {
    const text = messageInput.value.trim();
    if (text) {
        addMessage(text, 'user');
        socket.emit('message', { text });
        messageInput.value = '';
        log(`Sent: ${text}`);
    }
}

// Receive response
socket.on('response', (data) => {
    addMessage(data.text, 'bot');
    log(`Response (${data.type}): ${data.text}`);
});

// Receive log
socket.on('log', (text) => {
    log(text);
});

// Connection
socket.on('connect', () => {
    log('Connected to server');
});

socket.on('disconnect', () => {
    log('Disconnected from server');
});

// Add message to chat
function addMessage(text, type) {
    const msg = document.createElement('div');
    msg.className = `message ${type}`;
    msg.textContent = text;

    // Add timestamp
    const timestamp = document.createElement('span');
    timestamp.className = 'timestamp';
    timestamp.textContent = new Date().toLocaleTimeString();
    msg.appendChild(timestamp);

    // Add copy button for bot messages
    if (type === 'bot') {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.textContent = '📋';
        copyBtn.onclick = () => {
            navigator.clipboard.writeText(text);
            copyBtn.textContent = '✅';
            setTimeout(() => copyBtn.textContent = '📋', 1000);
        };
        msg.appendChild(copyBtn);
    }

    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
}

// Log to side panel
function log(text) {
    const timestamp = new Date().toLocaleTimeString();
    logOutput.textContent += `[${timestamp}] ${text}\n`;
    logOutput.scrollTop = logOutput.scrollHeight;
}

// Theme toggle
document.getElementById('themeToggle').addEventListener('click', () => {
    document.body.classList.toggle('light');
});

// Side tabs
document.querySelectorAll('.side-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.side-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.side-view').forEach(v => v.classList.add('hidden'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.view + 'View').classList.remove('hidden');
    });
});

// Live voice input with captions
let recognition;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let finalTranscript = '';

    recognition.onresult = (event) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        messageInput.value = finalTranscript + interimTranscript;
        if (finalTranscript && !interimTranscript) {
            // Final result, send message
            sendMessage();
            finalTranscript = '';
        }
    };

    recognition.onend = () => {
        micButton.classList.remove('active');
    };

    recognition.onerror = (event) => {
        log(`Speech recognition error: ${event.error}`);
        micButton.classList.remove('active');
    };

    micButton.addEventListener('click', () => {
        if (recognition) {
            finalTranscript = '';
            recognition.start();
            micButton.classList.add('active');
        }
    });
} else {
    micButton.disabled = true;
    log('Speech recognition not supported');
}

// Initial log
log('Assistant started');

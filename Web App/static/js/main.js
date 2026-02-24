/**
 * Gruha Alankara – Main JavaScript
 * 
 * Handles:
 * - Voice Assistant widget interactions
 * - Common UI utilities
 */

// ============================================================
// Voice Assistant
// ============================================================
(function initVoiceAssistant() {
    // Skip if studio.js handles its own voice assistant
    if (document.getElementById('studio-canvas')) return;

    const toggle = document.getElementById('voiceToggle');
    const panel = document.getElementById('voicePanel');
    const closeBtn = document.getElementById('closeVoicePanel');
    const input = document.getElementById('voiceInput');
    const sendBtn = document.getElementById('voiceSend');
    const messages = document.getElementById('voiceMessages');

    if (!toggle) return; // Not on a page with voice assistant

    // Toggle panel
    toggle.addEventListener('click', () => {
        panel.classList.toggle('open');
        toggle.classList.toggle('active');
        if (panel.classList.contains('open')) {
            input.focus();
        }
    });

    // Close panel
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            panel.classList.remove('open');
            toggle.classList.remove('active');
        });
    }

    // Send message
    function sendMessage() {
        const query = input.value.trim();
        if (!query) return;

        // Add user message
        appendMessage(query, 'user-msg');
        input.value = '';

        // Show typing indicator
        const typingId = 'typing-' + Date.now();
        appendMessage('<div class="spinner" style="width:20px;height:20px;border-width:2px;margin:0;"></div>', 'bot-msg', typingId);

        // Call API
        fetch('/api/voice-assist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        })
            .then(res => res.json())
            .then(data => {
                // Remove typing indicator
                const typingEl = document.getElementById(typingId);
                if (typingEl) typingEl.remove();

                // Add bot response
                appendMessage(data.text || 'I couldn\'t process that. Please try again.', 'bot-msg');

                // Play audio if available
                if (data.audio_url) {
                    const audio = new Audio(data.audio_url);
                    audio.volume = 0.7;
                    audio.play().catch(() => { }); // Ignore autoplay blocking
                }
            })
            .catch(err => {
                const typingEl = document.getElementById(typingId);
                if (typingEl) typingEl.remove();
                appendMessage('Sorry, I encountered an error. Please try again.', 'bot-msg');
                console.error('[Voice] Error:', err);
            });
    }

    function appendMessage(text, className, id = '') {
        const div = document.createElement('div');
        div.className = `voice-message ${className}`;
        div.innerHTML = text;
        if (id) div.id = id;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
})();

// ============================================================
// Intersection Observer for Fade-in Animations
// ============================================================
(function initFadeAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.glass-card, .feature-card').forEach(el => {
        observer.observe(el);
    });
})();

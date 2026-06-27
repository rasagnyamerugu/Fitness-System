
(function () {
    const btn = document.getElementById('chatbot-btn');
    const panel = document.getElementById('chatbot-panel');
    const messages = document.getElementById('chat-messages');
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');

    if (!btn || !panel) return;

    let isOpen = false;
    let isLoading = false;

    function setTextWithLineBreaks(el, text) {
        el.textContent = '';
        const parts = String(text || '').split('\n');
        parts.forEach((part, idx) => {
            if (idx) el.appendChild(document.createElement('br'));
            el.appendChild(document.createTextNode(part));
        });
    }

    function addBotMessage(text) {
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble bot';

        const label = document.createElement('div');
        label.className = 'bubble-label';
        label.textContent = 'GymTracker AI';

        const content = document.createElement('div');
        content.className = 'bubble-content';
        setTextWithLineBreaks(content, text);

        bubble.appendChild(label);
        bubble.appendChild(content);

        messages.appendChild(bubble);
        messages.scrollTop = messages.scrollHeight;
    }

    function addUserMessage(text) {
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble user';
        bubble.textContent = text;
        messages.appendChild(bubble);
        messages.scrollTop = messages.scrollHeight;
    }

    function showTyping() {
        const el = document.createElement('div');
        el.className = 'typing-indicator';
        el.id = 'typing-indicator';
        el.innerHTML = '<span></span><span></span><span></span>';
        messages.appendChild(el);
        messages.scrollTop = messages.scrollHeight;
    }

    function removeTyping() {
        const el = document.getElementById('typing-indicator');
        if (el) el.remove();
    }

    function getPageContent() {
        const main = document.querySelector('.main');
        return main ? main.innerText.trim() : document.body.innerText.trim();
    }
    btn.addEventListener('click', function () {
        isOpen = !isOpen;
        btn.classList.toggle('open', isOpen);
        panel.classList.toggle('open', isOpen);

        if (isOpen && messages.children.length === 0) {
            const pageName = document.title.replace('Gym Tracker —', '').trim();
            addBotMessage(
                "Hey! I'm your GymTracker AI assistant.\n" +
                "I can answer questions about the " + pageName + " page. What would you like to know?"
            );
        }
    });

    function sendMessage() {
        const text = input.value.trim();
        if (!text || isLoading) return;

        addUserMessage(text);
        input.value = '';
        isLoading = true;
        sendBtn.disabled = true;

        showTyping();

        fetch('/chatbot-api', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, context: getPageContent() })
        })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                removeTyping();
                addBotMessage(data.reply);
            })
            .catch(function () {
                removeTyping();
                addBotMessage('Sorry, something went wrong. Please try again.');
            })
            .finally(function () {
                isLoading = false;
                sendBtn.disabled = false;
                input.focus();
            });
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') sendMessage();
    });
})();
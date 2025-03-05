document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chatContainer');
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendMessage');
    const clearInputButton = document.getElementById('clearInput');
    const clearChatButton = document.getElementById('clearChat');
    const copyChatButton = document.getElementById('copyChat');
    const notificationBar = document.getElementById('notificationBar');

    function showNotification(message) {
        notificationBar.textContent = message;
        notificationBar.style.display = 'block';
        setTimeout(() => {
            notificationBar.style.display = 'none';
        }, 3000);
    }

    function addMessage(content, isUser = true) {
        const messageGroup = document.createElement('div');
        messageGroup.classList.add('message-group', isUser ? 'user-group' : 'system-group');
        
        const label = document.createElement('div');
        label.classList.add('message-label');
        label.textContent = isUser ? 'User' : 'System';
        
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', isUser ? 'user-message' : 'system-message');
        
        const copyButton = document.createElement('button');
        copyButton.classList.add('copy-button');
        copyButton.textContent = '📋';
        copyButton.setAttribute('aria-label', 'Copy message');
        copyButton.addEventListener('click', function() {
            navigator.clipboard.writeText(content).then(function() {
                showNotification('消息已复制到剪贴板！');
            }, function(err) {
                console.error('无法复制文本: ', err);
            });
        });
        
        messageElement.appendChild(copyButton);
        
        // 检查代码块并应用语法高亮
        const codeRegex = /```(\w+)?\s*([\s\S]*?)```/g;
        let lastIndex = 0;
        let match;
        
        while ((match = codeRegex.exec(content)) !== null) {
            // 添加代码块前的文本
            if (match.index > lastIndex) {
                messageElement.appendChild(document.createTextNode(content.slice(lastIndex, match.index)));
            }
            
            // 创建代码块
            const pre = document.createElement('pre');
            const code = document.createElement('code');
            if (match[1]) {
                code.className = `language-${match[1]}`;
            }
            code.textContent = match[2].trim();
            pre.appendChild(code);
            messageElement.appendChild(pre);
            
            lastIndex = match.index + match[0].length;
        }
        
        // 添加最后一个代码块后的剩余文本
        if (lastIndex < content.length) {
            messageElement.appendChild(document.createTextNode(content.slice(lastIndex)));
        }
        
        messageGroup.appendChild(label);
        messageGroup.appendChild(messageElement);
        
        chatContainer.appendChild(messageGroup);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // 应用语法高亮
        messageElement.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightBlock(block);
        });
    }

    function addThinkingMessage() {
        const messageGroup = document.createElement('div');
        messageGroup.classList.add('message-group', 'system-group');
        
        const label = document.createElement('div');
        label.classList.add('message-label');
        label.textContent = 'System';
        
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', 'system-message');
        
        const thinkingIndicator = document.createElement('div');
        thinkingIndicator.classList.add('thinking');
        
        const thinkingText = document.createTextNode('思考中...');
        
        messageElement.appendChild(thinkingIndicator);
        messageElement.appendChild(thinkingText);
        
        messageGroup.appendChild(label);
        messageGroup.appendChild(messageElement);
        
        chatContainer.appendChild(messageGroup);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        return messageGroup;
    }

    clearInputButton.addEventListener('click', function() {
        chatInput.value = '';
    });

    clearChatButton.addEventListener('click', function() {
        chatContainer.innerHTML = '';
        // 添加初始系统消息
        addMessage("您好！我是 StoryCanva 的 AI 助手，可以帮您创作故事、提供写作建议或回答问题。请告诉我您需要什么帮助？", false);
    });

    copyChatButton.addEventListener('click', function() {
        const chatText = Array.from(chatContainer.querySelectorAll('.message-group'))
            .map(group => {
                const label = group.querySelector('.message-label').textContent;
                const messageElement = group.querySelector('.chat-message');
                const message = Array.from(messageElement.childNodes)
                    .filter(node => node.nodeType === Node.TEXT_NODE || node.nodeName !== 'BUTTON')
                    .map(node => node.textContent.trim())
                    .join('');
                return `${label}: ${message}`;
            })
            .join('\n\n');
        navigator.clipboard.writeText(chatText).then(function() {
            showNotification('聊天记录已复制到剪贴板！');
        }, function(err) {
            console.error('无法复制文本: ', err);
        });
    });

    sendButton.addEventListener('click', function() {
        const message = chatInput.value.trim();
        if (message) {
            addMessage(message, true);
            chatInput.value = '';
            
            // 发送消息到后端
            const thinkingMessage = addThinkingMessage();
            
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('网络响应不正常');
                }
                return response.json();
            })
            .then(data => {
                // 移除思考中消息
                chatContainer.removeChild(thinkingMessage);
                
                // 添加AI回复
                addMessage(data.response, false);
            })
            .catch(error => {
                console.error('获取回复失败:', error);
                
                // 移除思考中消息
                chatContainer.removeChild(thinkingMessage);
                
                // 添加错误消息
                addMessage("抱歉，我遇到了一些问题，无法回应您的消息。请稍后再试。", false);
            });
        }
    });

    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    });

    // 为现有消息添加复制功能
    document.querySelectorAll('.copy-button').forEach(button => {
        button.addEventListener('click', function() {
            const messageText = this.nextSibling.textContent.trim();
            navigator.clipboard.writeText(messageText).then(function() {
                showNotification('消息已复制到剪贴板！');
            }, function(err) {
                console.error('无法复制文本: ', err);
            });
        });
    });
    
    // 添加初始系统消息
    if (chatContainer && chatContainer.children.length === 0) {
        addMessage("您好！我是 StoryCanva 的 AI 助手，可以帮您创作故事、提供写作建议或回答问题。请告诉我您需要什么帮助？", false);
    }
    
    // 添加暗黑模式切换功能
    const darkModeToggle = document.createElement('button');
    darkModeToggle.id = 'darkModeToggle';
    darkModeToggle.classList.add('btn', 'btn-outline-light', 'position-absolute', 'top-0', 'end-0', 'm-2');
    darkModeToggle.textContent = '🌙';
    darkModeToggle.setAttribute('aria-label', 'Toggle dark mode');
    
    document.querySelector('.navbar').appendChild(darkModeToggle);
    
    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        this.textContent = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chatContainer');
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendMessage');
    const clearInputButton = document.getElementById('clearInput');
    const clearChatButton = document.getElementById('clearChat');
    const copyChatButton = document.getElementById('copyChat');
    const notificationBar = document.getElementById('notificationBar');

    // 存储聊天历史
    let chatHistory = [];

    function showNotification(message) {
        notificationBar.textContent = message;
        notificationBar.style.display = 'block';
        setTimeout(() => {
            notificationBar.style.display = 'none';
        }, 3000);
    }

    function addMessage(content, isUser = true) {
        // 添加消息到历史记录
        chatHistory.push({
            role: isUser ? 'user' : 'assistant',
            content: content
        });

        const messageGroup = document.createElement('div');
        messageGroup.classList.add('message-group', isUser ? 'user-group' : 'system-group');
        
        const label = document.createElement('div');
        label.classList.add('message-label');
        label.textContent = isUser ? '用户' : '助手';
        
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

        return messageElement;
    }

    function addThinkingMessage() {
        const messageGroup = document.createElement('div');
        messageGroup.classList.add('message-group', 'system-group');
        
        const label = document.createElement('div');
        label.classList.add('message-label');
        label.textContent = '助手';
        
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

    // 创建流式响应消息容器
    function createStreamResponseContainer() {
        // 添加消息到历史记录（内容暂时为空）
        chatHistory.push({
            role: 'assistant',
            content: ''
        });

        const messageGroup = document.createElement('div');
        messageGroup.classList.add('message-group', 'system-group');
        
        const label = document.createElement('div');
        label.classList.add('message-label');
        label.textContent = '助手';
        
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', 'system-message');
        
        const copyButton = document.createElement('button');
        copyButton.classList.add('copy-button');
        copyButton.textContent = '📋';
        copyButton.setAttribute('aria-label', 'Copy message');
        copyButton.style.display = 'none'; // 初始隐藏复制按钮
        
        messageElement.appendChild(copyButton);
        
        messageGroup.appendChild(label);
        messageGroup.appendChild(messageElement);
        
        chatContainer.appendChild(messageGroup);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        return { messageGroup, messageElement, copyButton };
    }

    // 更新流式响应内容
    function updateStreamResponse(messageElement, content) {
        console.log("更新流式响应:", content.substring(0, 50) + (content.length > 50 ? "..." : ""));
        
        // 更新历史记录中最后一条消息的内容
        if (chatHistory.length > 0) {
            chatHistory[chatHistory.length - 1].content = content;
        }

        // 保留复制按钮
        const copyButton = messageElement.querySelector('.copy-button');
        
        // 完全清空元素内容
        messageElement.innerHTML = '';
        
        // 重新添加复制按钮
        if (copyButton) {
            messageElement.appendChild(copyButton);
            copyButton.style.display = 'none'; // 暂时隐藏，等内容加载完再显示
        }
        
        // 检查代码块并应用语法高亮
        const codeRegex = /```(\w+)?\s*([\s\S]*?)```/g;
        let lastIndex = 0;
        let match;
        
        while ((match = codeRegex.exec(content)) !== null) {
            // 添加代码块前的文本
            if (match.index > lastIndex) {
                const textNode = document.createTextNode(content.slice(lastIndex, match.index));
                messageElement.appendChild(textNode);
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
            const textNode = document.createTextNode(content.slice(lastIndex));
            messageElement.appendChild(textNode);
        }
        
        // 确保复制按钮在最前面
        if (copyButton) {
            messageElement.insertBefore(copyButton, messageElement.firstChild);
            copyButton.style.display = 'block';
            
            // 更新复制按钮的事件监听器
            copyButton.onclick = function() {
                navigator.clipboard.writeText(content).then(function() {
                    showNotification('消息已复制到剪贴板！');
                }, function(err) {
                    console.error('无法复制文本: ', err);
                });
            };
        }
        
        // 应用语法高亮
        messageElement.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightBlock(block);
        });
        
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    clearInputButton.addEventListener('click', function() {
        chatInput.value = '';
    });

    clearChatButton.addEventListener('click', function() {
        chatContainer.innerHTML = '';
        chatHistory = [];
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
            // 添加用户消息
            addMessage(message, true);
            chatInput.value = '';
            
            // 准备发送到后端的消息历史
            const messages = chatHistory.map(msg => ({
                role: msg.role,
                content: msg.content
            }));
            
            console.log("发送消息历史:", messages);
            
            // 创建流式响应容器
            const { messageElement, copyButton } = createStreamResponseContainer();
            
            // 使用 fetch 和 ReadableStream 处理流式响应
            fetch('/api/chat_stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    messages: messages
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('网络响应不正常');
                }
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let responseText = '';
                
                function readStream() {
                    return reader.read().then(({ done, value }) => {
                        if (done) {
                            console.log("流结束，最终响应:", responseText.substring(0, 50) + (responseText.length > 50 ? "..." : ""));
                            // 流结束，显示复制按钮
                            copyButton.style.display = 'block';
                            return;
                        }
                        
                        // 解码并添加到响应文本
                        const chunk = decoder.decode(value, { stream: true });
                        console.log("收到数据块:", chunk.substring(0, 50) + (chunk.length > 50 ? "..." : ""));
                        
                        try {
                            // 检查是否是JSON格式的错误消息
                            const jsonData = JSON.parse(chunk);
                            console.log("解析为JSON:", jsonData);
                            if (jsonData.error) {
                                responseText = jsonData.error;
                                updateStreamResponse(messageElement, responseText);
                                copyButton.style.display = 'block';
                                return;
                            }
                            // 如果是其他类型的JSON数据，可能需要特殊处理
                            if (jsonData.content) {
                                responseText += jsonData.content;
                            } else {
                                responseText += JSON.stringify(jsonData);
                            }
                        } catch (e) {
                            // 不是JSON，继续正常处理
                            responseText += chunk;
                        }
                        
                        // 更新UI
                        updateStreamResponse(messageElement, responseText);
                        
                        // 继续读取流
                        return readStream();
                    }).catch(error => {
                        console.error("读取流时出错:", error);
                        updateStreamResponse(messageElement, responseText + "\n\n[读取数据时出错]");
                        copyButton.style.display = 'block';
                    });
                }
                
                return readStream();
            })
            .catch(error => {
                console.error('获取回复失败:', error);
                
                // 添加错误消息
                updateStreamResponse(messageElement, "抱歉，我遇到了一些问题，无法回应您的消息。请稍后再试。");
                copyButton.style.display = 'block';
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
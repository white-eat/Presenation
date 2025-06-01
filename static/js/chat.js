document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    let currentSocket = null;

    if (!chatForm || !userInput || !chatBox) {
        console.error("无法找到聊天界面的关键元素");
        showErrorMessage('聊天界面加载失败，请刷新页面或联系管理员。');
        return;
    }

    // 初始化WebSocket连接
    // try {
    //     currentSocket = initWebSocket();
    // } catch (error) {
    //     console.error('WebSocket初始化失败:', error);
    //     showErrorMessage('无法连接到AI服务器，请确保服务已启动');
    // }

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const question = userInput.value.trim();    
        if (question === '') return;

        console.log("用户输入:", question); // 日志调试

        // 添加用户提问到聊天框
        const userMessage = document.createElement('div');
        userMessage.className = 'message user-message d-flex flex-column align-items-end';
        userMessage.innerHTML = `
            <div class="fw-bold text-primary mb-1">用户：</div>
            <div>${question}</div>
        `;
        chatBox.appendChild(userMessage);
        console.log("已添加用户消息"); // 日志调试

        // 创建加载中的AI回复占位符
        const aiMessageLoading = document.createElement('div');
        aiMessageLoading.className = 'message ai-message d-flex flex-column align-items-start';
        aiMessageLoading.innerHTML = `
            <div class="fw-bold text-success mb-1">AI：</div>
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatBox.appendChild(aiMessageLoading);

        // 清空输入框并滚动到底部
        userInput.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;

        // 发送请求到服务器获取AI回答
        if (currentSocket && currentSocket.readyState === WebSocket.OPEN) {
            console.log("通过WebSocket发送消息:", question); // 日志调试
            currentSocket.send(question);
        } else {
            console.warn("WebSocket不可用，尝试使用HTTP回退"); // 日志调试
            fetch(`/chat?message=${encodeURIComponent(question)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP错误: ' + response.status);
                    }
                    return response.text();
                })
                .then(data => {
                    console.log("收到HTTP响应:", data); // 日志调试
                    // 移除加载指示器并显示结果
                    if (chatBox.contains(aiMessageLoading)) {
                        chatBox.removeChild(aiMessageLoading);
                    }
                    displayAIMessage(data);
                })
                .catch(error => {
                    console.error('获取AI回答失败:', error); // 日志调试
                    // 移除加载指示器
                    if (chatBox.contains(aiMessageLoading)) {
                        chatBox.removeChild(aiMessageLoading);
                    }
                    showErrorMessage('无法获取AI回答，请检查服务器是否运行');
                });
        }
    });

    // 显示AI回复
    function displayAIMessage(message) {
        const aiMessage = document.createElement('div');
        aiMessage.className = 'message ai-message d-flex flex-column align-items-start';
        aiMessage.innerHTML = `
            <div class="fw-bold text-success mb-1">AI：</div>
            <div>${message}</div>
        `;
        chatBox.appendChild(aiMessage);

        // 滚动到底部
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // 显示错误信息
    function showErrorMessage(message) {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'message ai-message d-flex flex-column align-items-start';
        errorMessage.innerHTML = `
            <div class="fw-bold text-danger mb-1">错误：</div>
            <div>${message}</div>
        `;
        chatBox.appendChild(errorMessage);

        // 滚动到底部
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // 显示重新连接按钮
    function showReconnectButton() {
        const reconnectBtn = document.createElement('button');
        reconnectBtn.className = 'btn btn-outline-primary mt-2 mx-auto d-block';
        reconnectBtn.textContent = '重新连接';

        reconnectBtn.onclick = function () {
            try {
                currentSocket = initWebSocket();
                if (currentSocket && currentSocket.readyState === WebSocket.OPEN) {
                    this.remove();
                }
            } catch (error) {
                console.error('重新连接失败:', error);
            }
        };

        chatBox.appendChild(reconnectBtn);
    }
});

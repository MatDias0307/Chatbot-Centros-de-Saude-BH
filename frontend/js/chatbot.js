document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chat-form');
  const userInput = document.getElementById('user-input');
  const chatBox = document.getElementById('chat-box');

  let isBotTyping = false;
  let conversationHistory = [];

  scrollToBottom();

  chatForm.addEventListener('submit', handleFormSubmit);
  userInput.addEventListener('keydown', handleKeyDown);

  async function handleFormSubmit(e) {
    e.preventDefault();
    const userMessage = userInput.value.trim();
    if (!userMessage || isBotTyping) return;

    await processUserMessage(userMessage);
  }

  async function processUserMessage(message) {
    addMessage(message, 'user');
    userInput.value = '';
    conversationHistory.push({ sender: 'user', text: message });

    showTypingIndicator();

    try {
      const botResponse = await getBotResponse(message);

      removeTypingIndicator();
      addMessage(botResponse, 'bot');
      conversationHistory.push({ sender: 'bot', text: botResponse });
    } catch (error) {
      removeTypingIndicator();
      addMessage('Desculpe, estou com problemas técnicos no momento. Tente novamente mais tarde.', 'bot');
      console.error('Erro ao obter resposta:', error);
    }
  }

  function addMessage(text, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    
    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');
    // Use innerHTML para que as tags HTML sejam interpretadas
    messageContent.innerHTML = text;
    
    const messageTime = document.createElement('div');
    messageTime.classList.add('message-time');
    messageTime.textContent = formatTime(new Date());
    
    messageElement.appendChild(messageContent);
    messageElement.appendChild(messageTime);
    chatBox.appendChild(messageElement);
    
    scrollToBottom();
  }  

  function showTypingIndicator() {
    if (isBotTyping) return;

    isBotTyping = true;
    const typingElement = document.createElement('div');
    typingElement.classList.add('message', 'bot', 'typing');
    typingElement.id = 'typing-indicator';

    const dots = document.createElement('div');
    dots.classList.add('typing-dots');
    dots.innerHTML = '<span></span><span></span><span></span>';

    typingElement.appendChild(dots);
    chatBox.appendChild(typingElement);
    scrollToBottom();
  }

  function removeTypingIndicator() {
    isBotTyping = false;
    const typingElement = document.getElementById('typing-indicator');
    if (typingElement) {
      typingElement.remove();
    }
  }

  function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function formatTime(date) {
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event('submit'));
    }
  }

  async function getBotResponse(userText) {
    // const apiUrl = 'http://127.0.0.1:5000/api/chat';;
    const apiUrl = 'https://chatbot-centros-de-saude-bh-backend.onrender.com';

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText })
      });

      if (!response.ok) {
        throw new Error(`Erro na API: ${response.status}`);
      }

      const data = await response.json();
      return data.response || 'Desculpe, não consegui entender sua pergunta.';
    } catch (error) {
      console.error('Erro ao chamar backend:', error);
      return 'Ocorreu um erro ao se conectar com o servidor. Tente novamente mais tarde.';
    }
  }
});

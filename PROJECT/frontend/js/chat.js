/**
 * Chat Module — WebSocket connection, message rendering, streaming.
 */
const Chat = (() => {
  let ws = null;
  let currentAiBubble = null;
  let currentThinkingBlock = null;
  let isStreaming = false;
  let onPlanReady = null;
  let onStageChange = null;
  let onError = null;

  function init({ onPlan, onStage, onErr }) {
    onPlanReady = onPlan;
    onStageChange = onStage;
    onError = onErr;
  }

  function connect() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${location.host}/ws/chat`);

    ws.onopen = () => _setStatus('online');
    ws.onclose = () => {
      _setStatus('offline');
      setTimeout(connect, 3000);
    };
    ws.onerror = () => _setStatus('offline');
    ws.onmessage = (event) => _handleMessage(JSON.parse(event.data));
  }

  function startPipeline(occupation, idea) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      if (onError) onError('Not connected to server. Please refresh.');
      return;
    }

    addUserMessage(idea);
    isStreaming = true;

    ws.send(JSON.stringify({
      type: 'start',
      occupation: occupation,
      idea: idea,
    }));
  }

  function sendFollowUp(message) {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    addUserMessage(message);
    isStreaming = true;
    currentAiBubble = null;

    ws.send(JSON.stringify({ type: 'chat', message }));
  }

  function _handleMessage(data) {
    switch (data.type) {
      case 'stage':
        if (onStageChange) onStageChange(data.stage, data.label);
        _ensureAiBubble();
        break;

      case 'thinking':
        _appendThinking(data.content);
        break;

      case 'content':
        _appendContent(data.content);
        break;

      case 'info':
        _addInfoMessage(data.content);
        break;

      case 'stage_complete':
        currentAiBubble = null;
        currentThinkingBlock = null;
        break;

      case 'plan_ready':
        isStreaming = false;
        currentAiBubble = null;
        if (onPlanReady) onPlanReady(data.content, data.session_id);
        break;

      case 'response_complete':
        isStreaming = false;
        currentAiBubble = null;
        break;

      case 'error':
        isStreaming = false;
        if (onError) onError(data.message);
        break;
    }

    _scrollToBottom();
  }

  function _ensureAiBubble() {
    if (currentAiBubble) return;

    const chatArea = document.getElementById('chat-area');
    const msg = document.createElement('div');
    msg.className = 'message message--ai';
    msg.innerHTML = `
      <div class="message__avatar">🤖</div>
      <div class="message__bubble"><div class="msg-content"></div></div>
    `;
    chatArea.appendChild(msg);
    currentAiBubble = msg.querySelector('.msg-content');
    currentThinkingBlock = null;
  }

  function _appendThinking(text) {
    if (!currentAiBubble) _ensureAiBubble();

    if (!currentThinkingBlock) {
      const block = document.createElement('div');
      block.className = 'thinking-block';
      block.innerHTML = `
        <div class="thinking-block__header">Thinking</div>
        <div class="thinking-block__content"></div>
      `;
      block.addEventListener('click', () => block.classList.toggle('thinking-block--expanded'));
      currentAiBubble.appendChild(block);
      currentThinkingBlock = block.querySelector('.thinking-block__content');
    }

    currentThinkingBlock.textContent += text;
  }

  function _appendContent(text) {
    if (!currentAiBubble) _ensureAiBubble();
    currentThinkingBlock = null;

    // Find or create the text node after thinking blocks
    let textNode = currentAiBubble.querySelector('.content-text');
    if (!textNode) {
      textNode = document.createElement('div');
      textNode.className = 'content-text';
      currentAiBubble.appendChild(textNode);
    }

    textNode.innerHTML = _renderMarkdown(textNode.getAttribute('data-raw') + text);
    textNode.setAttribute('data-raw', (textNode.getAttribute('data-raw') || '') + text);
  }

  function addUserMessage(text) {
    const chatArea = document.getElementById('chat-area');
    const msg = document.createElement('div');
    msg.className = 'message message--user';
    msg.innerHTML = `
      <div class="message__avatar">👤</div>
      <div class="message__bubble">${_escapeHtml(text)}</div>
    `;
    chatArea.appendChild(msg);
    _scrollToBottom();
  }

  function addWelcomeMessage(occupation) {
    const chatArea = document.getElementById('chat-area');
    const msg = document.createElement('div');
    msg.className = 'message message--ai';
    msg.innerHTML = `
      <div class="message__avatar">🤖</div>
      <div class="message__bubble">
        <div class="content-text">
          <strong>Welcome, ${_escapeHtml(occupation)}!</strong><br><br>
          I'm Product Thinker — your AI product strategist. Tell me your rough product idea and I'll run a deep 4-stage analysis:<br><br>
          🧠 <strong>Brainstorm</strong> → 10 refined ideas<br>
          📊 <strong>Sentiment</strong> → market demand analysis<br>
          🔍 <strong>Niche</strong> → best opportunity<br>
          📋 <strong>MVP Plan</strong> → actionable blueprint<br><br>
          <em>What idea are you thinking about?</em>
        </div>
      </div>
    `;
    chatArea.appendChild(msg);
  }

  function _addInfoMessage(text) {
    const chatArea = document.getElementById('chat-area');
    const info = document.createElement('div');
    info.className = 'info-msg';
    info.textContent = text;
    chatArea.appendChild(info);
  }

  function _scrollToBottom() {
    const chatArea = document.getElementById('chat-area');
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function _escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function _renderMarkdown(text) {
    if (!text) return '';
    
    // Escape HTML first to prevent XSS
    let html = _escapeHtml(text);
    
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Headers
    html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');
    
    // Horizontal rules
    html = html.replace(/^---$/gm, '<hr>');
    
    // Blockquotes
    html = html.replace(/^&gt; (.*$)/gm, '<blockquote>$1</blockquote>');
    
    // Lists (unordered)
    // We handle lists line by line for simplicity in this regex approach
    const lines = html.split('\n');
    let inList = false;
    const processedLines = lines.map(line => {
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        const content = line.trim().substring(2);
        if (!inList) {
          inList = true;
          return '<ul><li>' + content + '</li>';
        }
        return '<li>' + content + '</li>';
      } else {
        if (inList) {
          inList = false;
          return '</ul>' + line;
        }
        return line;
      }
    });
    
    if (inList) processedLines.push('</ul>');
    html = processedLines.join('\n');
    
    // Line breaks (only if not inside a list or already handled)
    html = html.replace(/\n/g, '<br>');
    
    // Clean up empty line breaks before/after tags
    html = html.replace(/<br><\/ul>/g, '</ul>');
    html = html.replace(/<ul><br>/g, '<ul>');
    
    return html;
  }

  function _setStatus(status) {
    const dot = document.getElementById('status-dot');
    dot.className = 'status-dot';
    if (status === 'online')  { dot.classList.add('status-dot--online');  dot.title = 'Connected'; }
    if (status === 'offline') { dot.classList.add('status-dot--offline'); dot.title = 'Disconnected'; }
    if (status === 'loading') { dot.classList.add('status-dot--loading'); dot.title = 'Connecting...'; }
  }

  function getIsStreaming() { return isStreaming; }

  return { init, connect, startPipeline, sendFollowUp, addWelcomeMessage, getIsStreaming };
})();

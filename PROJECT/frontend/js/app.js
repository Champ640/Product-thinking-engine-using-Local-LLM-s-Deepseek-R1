/**
 * App — main application controller.
 * Coordinates occupation selector, chat, and plan viewer.
 */
document.addEventListener('DOMContentLoaded', () => {
  let selectedOccupation = null;
  let pipelineStarted = false;

  // Initialize modules
  Chat.init({
    onPlan: handlePlanReady,
    onStage: handleStageChange,
    onErr: handleError,
  });

  Chat.connect();

  OccupationSelector.init((occupation) => {
    selectedOccupation = occupation;
    _switchToChatScreen(occupation);
  });

  // Chat input handlers
  document.getElementById('send-btn').addEventListener('click', handleSend);
  document.getElementById('chat-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  // Action bar handlers
  document.getElementById('download-btn').addEventListener('click', () => PlanViewer.download());
  document.getElementById('restart-btn').addEventListener('click', handleRestart);

  // Check Ollama health on load
  _checkHealth();

  // --- Handlers ---

  function handleSend() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text || Chat.getIsStreaming()) return;

    input.value = '';

    if (!pipelineStarted) {
      pipelineStarted = true;
      input.placeholder = 'Ask a follow-up question...';
      Chat.startPipeline(selectedOccupation, text);
    } else {
      Chat.sendFollowUp(text);
    }
  }

  function handlePlanReady(planContent, sessionId) {
    PlanViewer.show(planContent, sessionId);
    document.getElementById('chat-input').placeholder = 'Ask a follow-up to refine the plan...';
  }

  function handleStageChange(stageId, label) {
    // Update stage progress indicators
    const stages = ['brainstorm', 'sentiment', 'niche', 'mvp'];
    const currentIndex = stages.indexOf(stageId);

    stages.forEach((s, i) => {
      const el = document.getElementById(`stage-${s}`);
      el.classList.remove('stage-item--active', 'stage-item--done');

      if (i < currentIndex) {
        el.classList.add('stage-item--done');
      } else if (i === currentIndex) {
        el.classList.add('stage-item--active');
      }
    });
  }

  function handleError(message) {
    const banner = document.getElementById('error-banner');
    banner.textContent = message;
    banner.classList.add('error-banner--visible');
    setTimeout(() => banner.classList.remove('error-banner--visible'), 8000);
  }

  function handleRestart() {
    pipelineStarted = false;
    PlanViewer.hide();
    document.getElementById('chat-area').innerHTML = '';
    document.getElementById('chat-input').placeholder = 'Describe your product idea...';

    // Reset stage indicators
    ['brainstorm', 'sentiment', 'niche', 'mvp'].forEach(s => {
      const el = document.getElementById(`stage-${s}`);
      el.classList.remove('stage-item--active', 'stage-item--done');
    });

    Chat.addWelcomeMessage(selectedOccupation);
  }

  // --- Internal ---

  function _switchToChatScreen(occupation) {
    document.getElementById('welcome-screen').classList.add('hidden');
    document.getElementById('chat-screen').classList.remove('hidden');

    // Show occupation badge
    const badge = document.getElementById('occupation-badge');
    badge.textContent = occupation;
    badge.style.display = 'inline-flex';

    Chat.addWelcomeMessage(occupation);
    document.getElementById('chat-input').focus();
  }

  async function _checkHealth() {
    try {
      const res = await fetch('/api/health');
      const data = await res.json();
      const dot = document.getElementById('status-dot');
      dot.className = 'status-dot';

      if (data.ollama) {
        dot.classList.add('status-dot--online');
        dot.title = `Ollama connected (${data.model})`;
      } else {
        dot.classList.add('status-dot--offline');
        dot.title = 'Ollama not reachable';
      }
    } catch {
      // WebSocket will handle reconnection display
    }
  }
});

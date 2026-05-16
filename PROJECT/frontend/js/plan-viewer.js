/**
 * Plan Viewer — renders and downloads the generated plan.md.
 */
const PlanViewer = (() => {
  let currentPlan = '';
  let currentSessionId = '';

  function show(planContent, sessionId) {
    currentPlan = planContent;
    currentSessionId = sessionId;

    const viewer = document.getElementById('plan-viewer');
    viewer.innerHTML = _renderPlanHtml(planContent);
    viewer.classList.add('plan-viewer--visible');

    document.getElementById('action-bar').classList.remove('hidden');
  }

  function download() {
    if (!currentPlan) return;

    const blob = new Blob([currentPlan], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'product-thinker-plan.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function hide() {
    const viewer = document.getElementById('plan-viewer');
    viewer.classList.remove('plan-viewer--visible');
    viewer.innerHTML = '';
    currentPlan = '';
    document.getElementById('action-bar').classList.add('hidden');
  }

  function _renderPlanHtml(markdown) {
    if (!markdown) return '';
    
    let html = _escapeHtml(markdown);
    
    // Headers
    html = html.replace(/^#### (.*$)/gm, '<h4>$1</h4>');
    html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');
    
    // Bold and italic
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Blockquotes
    html = html.replace(/^&gt; (.*$)/gm, '<blockquote>$1</blockquote>');
    
    // Horizontal rules
    html = html.replace(/^---$/gm, '<hr>');
    
    // Lists (unordered)
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
    
    // Line breaks
    html = html.replace(/\n/g, '<br>');
    
    // Clean up empty line breaks before/after tags
    html = html.replace(/<br><\/ul>/g, '</ul>');
    html = html.replace(/<ul><br>/g, '<ul>');
    
    return html;
  }

  function _escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  return { show, download, hide };
})();

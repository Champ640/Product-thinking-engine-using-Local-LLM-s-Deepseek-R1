/**
 * Occupation Selector — handles the welcome screen occupation cards.
 */
const OccupationSelector = (() => {
  let selectedOccupation = null;
  let onSelectCallback = null;

  function init(onSelect) {
    onSelectCallback = onSelect;
    _fetchAndRender();
  }

  async function _fetchAndRender() {
    try {
      const res = await fetch('/api/occupations');
      const data = await res.json();
      _renderCards(data.occupations);
    } catch {
      // Fallback if API is down
      _renderCards(_fallbackOccupations());
    }
  }

  function _renderCards(occupations) {
    const grid = document.getElementById('occupation-grid');
    grid.innerHTML = '';

    occupations.forEach(occ => {
      const card = document.createElement('div');
      card.className = 'occupation-card';
      card.id = `occ-${occ.id}`;
      card.innerHTML = `
        <span class="occupation-card__icon">${occ.icon}</span>
        <span class="occupation-card__label">${occ.label}</span>
      `;

      if (occ.id === 'other') {
        card.addEventListener('click', () => _showCustomInput());
      } else {
        card.addEventListener('click', () => _selectOccupation(occ.label, card));
      }

      grid.appendChild(card);
    });
  }

  function _selectOccupation(label, cardEl) {
    // Clear previous selection
    document.querySelectorAll('.occupation-card').forEach(c => c.classList.remove('occupation-card--selected'));
    cardEl.classList.add('occupation-card--selected');
    selectedOccupation = label;

    // Brief delay for visual feedback, then proceed
    setTimeout(() => {
      if (onSelectCallback) onSelectCallback(selectedOccupation);
    }, 300);
  }

  function _showCustomInput() {
    document.getElementById('custom-occupation-area').style.display = 'flex';
    document.getElementById('custom-occupation-input').focus();

    document.getElementById('custom-occupation-btn').addEventListener('click', () => {
      const val = document.getElementById('custom-occupation-input').value.trim();
      if (val && onSelectCallback) {
        selectedOccupation = val;
        onSelectCallback(selectedOccupation);
      }
    });

    document.getElementById('custom-occupation-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        document.getElementById('custom-occupation-btn').click();
      }
    });
  }

  function _fallbackOccupations() {
    return [
      { id: 'software-developer', label: 'Software Developer', icon: '💻' },
      { id: 'designer', label: 'Designer', icon: '🎨' },
      { id: 'marketing', label: 'Marketing / Growth', icon: '📈' },
      { id: 'finance', label: 'Finance / Accounting', icon: '💰' },
      { id: 'healthcare', label: 'Healthcare Professional', icon: '🏥' },
      { id: 'educator', label: 'Educator / Teacher', icon: '📚' },
      { id: 'content-creator', label: 'Content Creator / Writer', icon: '✍️' },
      { id: 'ecommerce', label: 'E-Commerce / Retail', icon: '🛒' },
      { id: 'freelancer', label: 'Freelancer / Consultant', icon: '🧑‍💼' },
      { id: 'student', label: 'Student / Researcher', icon: '🎓' },
      { id: 'other', label: 'Other', icon: '✏️' },
    ];
  }

  function getSelected() { return selectedOccupation; }

  return { init, getSelected };
})();

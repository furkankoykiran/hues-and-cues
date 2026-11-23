(() => {
  // ───── State ─────
  const state = {
    lang: localStorage.getItem('lang') || 'en',
    theme: localStorage.getItem('theme') || 'light',
    teams: [],
    currentTeam: 0,
    targetCell: null,
    guessCell: null,
    isTargetVisible: true,
    canGuess: false
  };
  let i18n = {};

  // ───── Element References ─────
  const htmlEl = document.documentElement;
  const themeBtn = document.getElementById('themeToggleBtn');
  const langSelect = document.getElementById('langSelect');
  const setupSection = document.getElementById('setup');
  const gameSection = document.getElementById('game');
  const teamCountIn = document.getElementById('teamCount');
  const teamNamesDiv = document.getElementById('teamNames');
  const startBtn = document.getElementById('startBtn');
  const scoreboardDiv = document.getElementById('scoreboard');
  const board = document.getElementById('board');
  const clueText = document.getElementById('clueText');
  const toggleBtn = document.getElementById('toggleBtn');
  const nextBtn = document.getElementById('nextBtn');
  const newGameBtn = document.getElementById('newGameBtn');
  const resultDisplay = document.getElementById('resultDisplay');
  const modal = document.getElementById('howToPlayModal');
  const helpBtn = document.getElementById('helpBtn');
  const closeModal = document.querySelector('.close');

  // ───── Theme ─────
  function applyTheme(t) {
    htmlEl.setAttribute('data-theme', t);
    themeBtn.textContent = t === 'light' ? '🌙' : '☀️';
    localStorage.setItem('theme', t);
  }
  
  themeBtn.addEventListener('click', () => {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    applyTheme(state.theme);
  });

  // ───── i18n ─────
  async function loadLocale(lang) {
    const res = await fetch(`locales/${lang}.json`);
    return res.json();
  }
  
  async function applyLocale(lang) {
    i18n = await loadLocale(lang);
    document.querySelectorAll('[data-i18n]').forEach(el => {
      el.textContent = i18n[el.dataset.i18n] || el.textContent;
    });
    // Keep the document language and title in sync with the visible interface.
    htmlEl.lang = lang;
    document.title = `${i18n.title} — ${i18n.subtitle}`;
    localStorage.setItem('lang', lang);
  }
  
  langSelect.value = state.lang;
  langSelect.addEventListener('change', () => {
    state.lang = langSelect.value;
    applyLocale(state.lang);
  });

  // ───── Setup Screen ─────
  function renderTeamInputs() {
    teamNamesDiv.innerHTML = '';
    for (let i = 0; i < +teamCountIn.value; i++) {
      const inp = document.createElement('input');
      inp.type = 'text';
      inp.placeholder = `${i+1}. ${i18n.teamName || 'Team'}`;
      inp.className = 'team-input';
      teamNamesDiv.append(inp);
    }
  }
  
  teamCountIn.addEventListener('input', renderTeamInputs);

  startBtn.addEventListener('click', () => {
    // Read teams
    state.teams = Array.from(teamNamesDiv.children).map(i => ({
      name: i.value || i.placeholder, score: 0
    }));
    
    if (state.teams.length === 0) {
      state.teams = [{ name: i18n.oneTeam || 'Individual', score: 0 }];
    }
    
    setupSection.hidden = true;
    gameSection.hidden = false;
    renderScoreboard();
    startRound();
  });

  // ───── Scoreboard ─────
  function renderScoreboard() {
    scoreboardDiv.innerHTML = state.teams.map((t, i) =>
      `<div${i === state.currentTeam ? ' class="current"' : ''}>${t.name}: ${t.score}</div>`
    ).join('');
  }

  // ───── Color Board Creation ─────
  function createBoard() {
    board.innerHTML = '';
    const width = 24;
    const height = 20;
    
    // Create the board cells
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const div = document.createElement("div");
        const hue = Math.floor((x / width) * 360);
        const sat = 100;
        const light = Math.floor(25 + (y / height) * 60);
        
        div.className = "cell";
        div.style.backgroundColor = `hsl(${hue}, ${sat}%, ${light}%)`;
        div.dataset.x = x;
        div.dataset.y = y;
        div.dataset.hue = hue;
        div.dataset.sat = sat;
        div.dataset.light = light;
        
        board.appendChild(div);
        
        div.addEventListener("click", () => {
          if (!state.canGuess) return;
          guessColor(div);
        });
      }
    }
  }

  // ───── Start New Round ─────
  function startRound() {
    // Clear previous guesses
    document.querySelectorAll('.cell').forEach(cell => {
      cell.classList.remove('selected', 'guess');
    });
    
    // Select a random cell as target
    const cells = document.querySelectorAll('.cell');
    state.targetCell = cells[Math.floor(Math.random() * cells.length)];
    state.guessCell = null;
    
    // Get a clue in the current language
    const currentLangClues = clues[state.lang] || clues['en']; // Fallback to English
    const randomClue = currentLangClues[Math.floor(Math.random() * currentLangClues.length)];
    
    clueText.textContent = randomClue;
    resultDisplay.textContent = '';
    
    toggleBtn.textContent = i18n.hideTarget || 'Hide Target';
    state.isTargetVisible = true;
    state.canGuess = false;
    
    // Mark target cell
    state.targetCell.classList.add('selected');
  }

  // ───── Calculate Score ─────
  function calcScore(guessCell, targetCell) {
    const dx = guessCell.dataset.x - targetCell.dataset.x;
    const dy = guessCell.dataset.y - targetCell.dataset.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    
    // Points based on distance
    if (dist < 1) return 5;     // Direct hit
    if (dist < 2) return 4;     // Very close
    if (dist < 3) return 3;     // Close
    if (dist < 4) return 2;     // Not far
    if (dist < 6) return 1;     // Far
    return 0;                   // Very far
  }

  // ───── Guess Handler ─────
  function guessColor(guessCell) {
    // Remove previous guess
    if (state.guessCell) {
      state.guessCell.classList.remove('guess');
    }
    
    // Mark new guess
    state.guessCell = guessCell;
    state.guessCell.classList.add('guess');
    
    // If the target is visible, calculate score immediately
    if (state.isTargetVisible) {
      const score = calcScore(state.guessCell, state.targetCell);
      state.teams[state.currentTeam].score += score;
      
      resultDisplay.textContent = `${i18n.score || 'Score'}: ${score} ${i18n.points || 'Points'}`;
      renderScoreboard();
    }
  }

  // ───── Buttons ─────
  toggleBtn.addEventListener('click', () => {
    if (state.isTargetVisible) {
      // Hide target
      state.targetCell.classList.remove('selected');
      toggleBtn.textContent = i18n.revealTarget || 'Reveal Target';
      state.canGuess = true;
    } else {
      // Show target and calculate score if there's a guess
      state.targetCell.classList.add('selected');
      toggleBtn.textContent = i18n.hideTarget || 'Hide Target';
      state.canGuess = false;
      
      if (state.guessCell) {
        const score = calcScore(state.guessCell, state.targetCell);
        state.teams[state.currentTeam].score += score;
        
        resultDisplay.textContent = `${i18n.score || 'Score'}: ${score} ${i18n.points || 'Points'}`;
        renderScoreboard();
      }
    }
    
    state.isTargetVisible = !state.isTargetVisible;
  });

  nextBtn.addEventListener('click', () => {
    state.currentTeam = (state.currentTeam + 1) % state.teams.length;
    renderScoreboard();
    startRound();
  });

  newGameBtn.addEventListener('click', () => {
    state.teams.forEach(t => t.score = 0);
    state.currentTeam = 0;
    renderScoreboard();
    startRound();
  });

  // ───── Modal Controls ─────
  helpBtn.addEventListener('click', () => {
    modal.style.display = 'flex';
  });
  
  closeModal.addEventListener('click', () => {
    modal.style.display = 'none';
  });

  // The close control is a span with role="button", so support the keyboard too.
  closeModal.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      modal.style.display = 'none';
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.style.display === 'flex') {
      modal.style.display = 'none';
    }
  });
  
  window.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
    }
  });

  // ───── Init ─────
  function initialize() {
    createBoard();
    applyTheme(state.theme);
    applyLocale(state.lang).then(renderTeamInputs);
  }
  
  // Start the game when the DOM is loaded
  document.addEventListener('DOMContentLoaded', initialize);
})(); 
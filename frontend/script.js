let API_URL = 'http://localhost:5000/api';

const pokemonImageMap = {
    'scryther': 'Scyther',
    'evevee': 'Eevee',
    'diglett': 'Digglet',
    'lickitung': 'Luckitung'
};

function getPokemonImageName(pokemonName) {
    const normalized = pokemonName.toLowerCase();
    if (pokemonImageMap[normalized]) {
        return pokemonImageMap[normalized];
    }
    return pokemonName.charAt(0).toUpperCase() + pokemonName.slice(1);
}

function getAPIUrl() {
    const savedUrl = localStorage.getItem('api_url');
    if (savedUrl) {
        let url = savedUrl.trim();
        if (!url.endsWith('/api')) {
            url = url.endsWith('/') ? url + 'api' : url + '/api';
        }
        return url;
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    const apiUrlParam = urlParams.get('api_url');
    if (apiUrlParam) {
        let url = apiUrlParam.trim();
        if (!url.endsWith('/api')) {
            url = url.endsWith('/') ? url + 'api' : url + '/api';
        }
        localStorage.setItem('api_url', url);
        return url;
    }
    
    return 'http://localhost:5000/api';
}

function setAPIUrl(url) {
    let cleanUrl = url.trim();
    if (!cleanUrl) {
        cleanUrl = 'http://localhost:5000/api';
    }
    if (!cleanUrl.endsWith('/api')) {
        cleanUrl = cleanUrl.endsWith('/') ? cleanUrl + 'api' : cleanUrl + '/api';
    }
    API_URL = cleanUrl;
    localStorage.setItem('api_url', cleanUrl);
    console.log('API URL updated to:', API_URL);
    loadPokemonList();
}

API_URL = getAPIUrl();

let pokemonList = [];
let pokemonData = {};
let currentTeam = 1;
let currentSlot = 0;
let teams = {
    1: [null, null, null],
    2: [null, null, null]
};

// Load Pokemon list
async function loadPokemonList() {
    try {
        console.log('Loading Pokemon list from:', `${API_URL}/pokemon`);
        
        const response = await fetch(`${API_URL}/pokemon`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            mode: 'cors'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.pokemon || !Array.isArray(data.pokemon)) {
            throw new Error('Invalid response format');
        }
        
        pokemonList = data.pokemon;
        
        // Preload all Pokemon stats
        await loadAllPokemonStats();
        
        // Populate selection modal
        populatePokemonModal();
        
        hideError();
        
    } catch (error) {
        console.error('Error loading Pokemon list:', error);
        showError(`Failed to load Pokemon list. Error: ${error.message}. Make sure the API server is running at ${API_URL.replace('/api', '')}.`);
    }
}

// Load all Pokemon stats
async function loadAllPokemonStats() {
    for (const pokemon of pokemonList) {
        try {
            const response = await fetch(`${API_URL}/pokemon/${pokemon}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                mode: 'cors'
            });
            
            if (response.ok) {
                const data = await response.json();
                pokemonData[pokemon] = data;
            }
        } catch (error) {
            console.error(`Error loading stats for ${pokemon}:`, error);
        }
    }
}

// Populate Pokemon selection modal
function populatePokemonModal(filter = '') {
    const grid = document.getElementById('pokemon-grid');
    if (!grid) {
        console.error('Pokemon grid not found!');
        return;
    }
    grid.innerHTML = '';
    
    const filtered = pokemonList.filter(p => {
        if (!filter) return true;
        return p.toLowerCase().includes(filter.toLowerCase());
    });
    
    filtered.forEach(pokemon => {
        const card = document.createElement('div');
        card.className = 'pokemon-card-select';
        card.onclick = () => selectPokemon(pokemon);
        
        // Get the Pokemon image filename
        const imageName = getPokemonImageName(pokemon);
        const imagePath = `images/${imageName}.png`;
        const displayName = pokemon.charAt(0).toUpperCase() + pokemon.slice(1);
        
        card.innerHTML = `
            <img src="${imagePath}" alt="${displayName}" class="pokemon-card-image" onerror="this.style.display='none'">
            <div class="card-name">${displayName}</div>
        `;
        
        grid.appendChild(card);
    });
}

// Open Pokemon selection modal
function openPokemonModal(team, slot) {
    currentTeam = team;
    currentSlot = slot;
    const modal = document.getElementById('pokemon-modal');
    if (!modal) {
        console.error('Modal element not found!');
        return;
    }
    modal.classList.remove('hidden');
    const searchInput = document.getElementById('pokemon-search');
    if (searchInput) {
        searchInput.value = '';
        searchInput.focus();
    }
    populatePokemonModal();
}

// Close Pokemon selection modal
function closePokemonModal() {
    document.getElementById('pokemon-modal').classList.add('hidden');
}

// Select Pokemon and add to team
function selectPokemon(pokemon) {
    if (teams[currentTeam][currentSlot] === pokemon) {
        closePokemonModal();
        return;
    }
    
    // Check if Pokemon is already in this team
    if (teams[currentTeam].includes(pokemon)) {
        showError(`${capitalize(pokemon)} is already in Team ${currentTeam}!`);
        return;
    }
    
    teams[currentTeam][currentSlot] = pokemon;
    renderTeamSlot(currentTeam, currentSlot);
    closePokemonModal();
    checkPredictButton();
}

// Remove Pokemon from team
function removePokemon(team, slot) {
    teams[team][slot] = null;
    renderTeamSlot(team, slot);
    checkPredictButton();
}

// Render a team slot
function renderTeamSlot(team, slot) {
    const slotElement = document.querySelector(`[data-team="${team}"][data-slot="${slot}"]`);
    
    if (!teams[team][slot]) {
        slotElement.className = 'team-slot empty';
        slotElement.innerHTML = '<div class="slot-placeholder">+ Add Pokemon</div>';
        slotElement.onclick = () => openPokemonModal(team, slot);
        return;
    }
    
    const pokemon = teams[team][slot];
    const data = pokemonData[pokemon];
    
    if (!data) {
        slotElement.className = 'team-slot empty';
        slotElement.innerHTML = '<div class="slot-placeholder">Loading...</div>';
        return;
    }
    
    slotElement.className = 'team-slot filled';
    
    const imageName = getPokemonImageName(pokemon);
    const imagePath = `images/${imageName}.png`;
    const displayName = pokemon.charAt(0).toUpperCase() + pokemon.slice(1);
    
    slotElement.innerHTML = `
        <div class="pokemon-card">
            <div class="pokemon-card-header">
                <div class="pokemon-name">${displayName}</div>
                <button class="remove-btn" onclick="removePokemon(${team}, ${slot}); event.stopPropagation();">Remove</button>
            </div>
            <div class="pokemon-card-content">
                <img src="${imagePath}" alt="${displayName}" class="pokemon-team-image" onerror="console.error('Failed to load image:', this.src);">
                <div class="pokemon-stats">
                    <div class="stat-row">
                        <span class="stat-label">HP:</span>
                        <span class="stat-value">${data.stats.hp}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Attack:</span>
                        <span class="stat-value">${data.stats.attack}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Defense:</span>
                        <span class="stat-value">${data.stats.defense}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Sp. Attack:</span>
                        <span class="stat-value">${data.stats.sp_attack}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Sp. Defense:</span>
                        <span class="stat-value">${data.stats.sp_defense}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Speed:</span>
                        <span class="stat-value">${data.stats.speed}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Total:</span>
                        <span class="stat-value">${data.stats.total}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    slotElement.onclick = () => openPokemonModal(team, slot);
}

// Check if predict button should be enabled
function checkPredictButton() {
    const team1HasPokemon = teams[1].some(p => p !== null);
    const team2HasPokemon = teams[2].some(p => p !== null);
    const predictBtn = document.getElementById('predict-btn');
    
    predictBtn.disabled = !team1HasPokemon || !team2HasPokemon;
}

// Predict battle
async function predictBattle() {
    const team1 = teams[1].filter(p => p !== null);
    const team2 = teams[2].filter(p => p !== null);
    
    if (!team1.length || !team2.length) {
        showError('Both teams need at least one Pokemon!');
        return;
    }
    
    const weather = document.getElementById('weather').value;
    const terrain = document.getElementById('terrain').value;
    const hazards = document.getElementById('hazards').value;
    
    const predictBtn = document.getElementById('predict-btn');
    predictBtn.disabled = true;
    predictBtn.textContent = 'Predicting...';
    
    hideError();
    
    try {
        console.log('Predicting battle:', { team1, team2, weather, terrain, hazards });
        
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            mode: 'cors',
            body: JSON.stringify({
                team1,
                team2,
                weather,
                terrain,
                hazards
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayResults(result);
        } else {
            showError(result.error || 'Prediction failed');
        }
    } catch (error) {
        console.error('Error predicting battle:', error);
        showError('Failed to connect to prediction server. Make sure the API is running.');
    } finally {
        predictBtn.disabled = false;
        predictBtn.textContent = 'Predict Winner';
    }
}

// Display prediction results
function displayResults(result) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.classList.remove('hidden');
    
    const winner = result.winner === 'team1' ? 'Team 1' : 'Team 2';
    document.getElementById('winner-name').textContent = `${winner} Wins!`;
    
    const confidence = Math.round(result.confidence * 100);
    document.getElementById('confidence').textContent = confidence;
    document.getElementById('confidence-bar').style.width = `${confidence}%`;
    
    const team1Prob = Math.round(result.probabilities.team1 * 100);
    const team2Prob = Math.round(result.probabilities.team2 * 100);
    
    document.getElementById('team1-prob-value').textContent = `${team1Prob}%`;
    document.getElementById('team1-prob-bar').style.width = `${team1Prob}%`;
    
    document.getElementById('team2-prob-value').textContent = `${team2Prob}%`;
    document.getElementById('team2-prob-bar').style.width = `${team2Prob}%`;
    
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

// Hide error message
function hideError() {
    document.getElementById('error').classList.add('hidden');
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Initialise on page load
document.addEventListener('DOMContentLoaded', () => {
    // Initialise team slots
    for (let team = 1; team <= 2; team++) {
        for (let slot = 0; slot < 3; slot++) {
            renderTeamSlot(team, slot);
        }
    }
    
    // Pokemon search
    document.getElementById('pokemon-search').addEventListener('input', (e) => {
        populatePokemonModal(e.target.value);
    });
    
    // Modal close handlers
    document.querySelector('.close-modal').addEventListener('click', closePokemonModal);
    document.getElementById('pokemon-modal').addEventListener('click', (e) => {
        if (e.target.id === 'pokemon-modal') {
            closePokemonModal();
        }
    });
    
    // Predict button
    document.getElementById('predict-btn').addEventListener('click', predictBattle);
    
    // Load Pokemon list
    loadPokemonList();
});

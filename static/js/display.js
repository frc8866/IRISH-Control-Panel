// Audience Display JavaScript - Polls for real-time updates
let lastUpdateTime = null;

// Fetch current scores and update display
function fetchScores() {
    fetch('/api/score')
        .then(response => response.json())
        .then(data => {
            updateDisplay(data);
            updateLastUpdateTime();
        })
        .catch(error => {
            console.error('Error fetching scores:', error);
        });
}

// Update the display with current scores
function updateDisplay(data) {
    // Red alliance
    document.getElementById('display_red_bucket').textContent = data.red_bucket || 0;
    document.getElementById('display_red_hp').textContent = data.red_hp || 0;
    document.getElementById('display_red_bench').textContent = data.red_bench || 0;
    document.getElementById('display_red_fouls').textContent = data.red_fouls || 0;
    document.getElementById('display_red_and_one').textContent = data.red_and_one_count || 0;
    document.getElementById('display_red_total').textContent = data.red_total || 0;
    
    // Show/hide red bonus indicator
    const redBonusIndicator = document.getElementById('red_bonus_indicator');
    if (data.red_bonus_active) {
        redBonusIndicator.classList.add('active');
    } else {
        redBonusIndicator.classList.remove('active');
    }
    
    // Blue alliance
    document.getElementById('display_blue_bucket').textContent = data.blue_bucket || 0;
    document.getElementById('display_blue_hp').textContent = data.blue_hp || 0;
    document.getElementById('display_blue_bench').textContent = data.blue_bench || 0;
    document.getElementById('display_blue_fouls').textContent = data.blue_fouls || 0;
    document.getElementById('display_blue_and_one').textContent = data.blue_and_one_count || 0;
    document.getElementById('display_blue_total').textContent = data.blue_total || 0;
    
    // Show/hide blue bonus indicator
    const blueBonusIndicator = document.getElementById('blue_bonus_indicator');
    if (data.blue_bonus_active) {
        blueBonusIndicator.classList.add('active');
    } else {
        blueBonusIndicator.classList.remove('active');
    }
}

// Update the last update timestamp
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('last_update').textContent = timeString;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    fetchScores();
    // Poll for updates every 1 second for real-time display
    setInterval(fetchScores, 1000);
});

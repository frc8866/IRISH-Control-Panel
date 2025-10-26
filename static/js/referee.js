// Referee Panel JavaScript
let currentScores = {};

// Fetch current scores and update display
function fetchScores() {
    fetch('/api/score')
        .then(response => response.json())
        .then(data => {
            currentScores = data;
            updateDisplay(data);
        })
        .catch(error => console.error('Error fetching scores:', error));
}

// Update the display with current scores
function updateDisplay(data) {
    // Red alliance
    document.getElementById('red_bucket').textContent = data.red_bucket || 0;
    document.getElementById('red_hp').textContent = data.red_hp || 0;
    document.getElementById('red_bench').textContent = data.red_bench || 0;
    document.getElementById('red_fouls_given').textContent = data.blue_fouls || 0; // Red fouls go to blue
    document.getElementById('red_and_one_count').textContent = data.red_and_one_count || 0;
    document.getElementById('red_total').textContent = data.red_total || 0;
    
    // Update red bonus status
    const redBonusStatus = document.getElementById('red_bonus_status');
    if (data.red_bonus_active) {
        redBonusStatus.textContent = 'ACTIVE (2x multiplier)';
        redBonusStatus.style.color = '#ff4444';
    } else {
        redBonusStatus.textContent = 'INACTIVE';
        redBonusStatus.style.color = '#666';
    }
    
    // Blue alliance
    document.getElementById('blue_bucket').textContent = data.blue_bucket || 0;
    document.getElementById('blue_hp').textContent = data.blue_hp || 0;
    document.getElementById('blue_bench').textContent = data.blue_bench || 0;
    document.getElementById('blue_fouls_given').textContent = data.red_fouls || 0; // Blue fouls go to red
    document.getElementById('blue_and_one_count').textContent = data.blue_and_one_count || 0;
    document.getElementById('blue_total').textContent = data.blue_total || 0;
    
    // Update blue bonus status
    const blueBonusStatus = document.getElementById('blue_bonus_status');
    if (data.blue_bonus_active) {
        blueBonusStatus.textContent = 'ACTIVE (2x multiplier)';
        blueBonusStatus.style.color = '#4444ff';
    } else {
        blueBonusStatus.textContent = 'INACTIVE';
        blueBonusStatus.style.color = '#666';
    }
}

// Update a specific score field
function updateScore(field, delta) {
    const currentValue = currentScores[field] || 0;
    const newValue = Math.max(0, currentValue + delta); // Don't go below 0
    
    const updateData = {};
    updateData[field] = newValue;
    
    fetch('/api/score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
    })
    .then(response => response.json())
    .then(data => {
        currentScores = data;
        updateDisplay(data);
    })
    .catch(error => console.error('Error updating score:', error));
}

// Increment AND ONE counter
function incrementAndOne(alliance) {
    const field = alliance + '_and_one_count';
    const bonusField = alliance + '_bonus_active';
    const currentCount = currentScores[field] || 0;
    const newCount = currentCount + 1;
    
    const updateData = {};
    updateData[field] = newCount;
    
    // Check if we need to activate bonus (every 3 AND ONEs)
    if (newCount > 0 && newCount % 3 === 0) {
        updateData[bonusField] = 1;
        // Set timer to deactivate after 15 seconds
        setTimeout(() => deactivateBonus(alliance), 15000);
    }
    
    fetch('/api/score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
    })
    .then(response => response.json())
    .then(data => {
        currentScores = data;
        updateDisplay(data);
    })
    .catch(error => console.error('Error updating AND ONE:', error));
}

// Decrement AND ONE counter
function decrementAndOne(alliance) {
    const field = alliance + '_and_one_count';
    const currentCount = currentScores[field] || 0;
    if (currentCount > 0) {
        const newCount = currentCount - 1;
        
        const updateData = {};
        updateData[field] = newCount;
        
        fetch('/api/score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        })
        .then(response => response.json())
        .then(data => {
            currentScores = data;
            updateDisplay(data);
        })
        .catch(error => console.error('Error updating AND ONE:', error));
    }
}

// Deactivate bonus multiplier
function deactivateBonus(alliance) {
    const bonusField = alliance + '_bonus_active';
    const updateData = {};
    updateData[bonusField] = 0;
    
    fetch('/api/score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
    })
    .then(response => response.json())
    .then(data => {
        currentScores = data;
        updateDisplay(data);
    })
    .catch(error => console.error('Error deactivating bonus:', error));
}

// Reset all scores
function resetScores() {
    if (confirm('Are you sure you want to reset all scores to zero?')) {
        fetch('/api/reset', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            currentScores = data;
            updateDisplay(data);
        })
        .catch(error => console.error('Error resetting scores:', error));
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    fetchScores();
    // Poll for updates every 2 seconds
    setInterval(fetchScores, 2000);
});

// Admin Panel JavaScript
const socket = io();

// Toast notification system
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => container.removeChild(toast), 300);
    }, duration);
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        
        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // Load data for the tab
        switch(tabName) {
            case 'matches': loadMatches(); break;
            case 'teams': loadTeams(); break;
            case 'rankings': loadRankings(); break;
            case 'events': loadMatchEvents(); break;
        }
    });
});

// Modal functions
function openModal(modalId) {
    document.getElementById(modalId).classList.add('show');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

// MATCHES FUNCTIONS
async function loadMatches() {
    try {
        const response = await fetch('/api/matches');
        const matches = await response.json();
        
        const tbody = document.getElementById('matches-tbody');
        
        if (matches.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="no-data">No matches found</td></tr>';
            return;
        }
        
        tbody.innerHTML = '';
        matches.forEach(match => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${match.id}</td>
                <td>${match.match_number}</td>
                <td><span class="badge badge-blue">${match.match_type}</span></td>
                <td>${getTeamNumbers(match.red_team1, match.red_team2)}</td>
                <td>${getTeamNumbers(match.blue_team1, match.blue_team2)}</td>
                <td><span class="badge badge-red">${match.red_score}</span></td>
                <td><span class="badge badge-blue">${match.blue_score}</span></td>
                <td><span class="badge badge-${getStatusColor(match.status)}">${match.status}</span></td>
                <td class="action-buttons">
                    <button class="btn btn-primary btn-sm" onclick="editMatch(${match.id})">Edit</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteMatch(${match.id})">Delete</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading matches:', error);
        showToast('Error loading matches', 'error');
    }
}

function getTeamNumbers(team1, team2) {
    const t1 = team1 ? team1.number : '?';
    const t2 = team2 ? team2.number : '?';
    return `${t1} / ${t2}`;
}

function getStatusColor(status) {
    if (status === 'completed') return 'success';
    if (status === 'in_progress') return 'warning';
    return 'blue';
}

async function editMatch(matchId) {
    try {
        const response = await fetch('/api/matches');
        const matches = await response.json();
        const match = matches.find(m => m.id === matchId);
        
        if (!match) {
            showToast('Match not found', 'error');
            return;
        }
        
        document.getElementById('edit-match-id').value = match.id;
        document.getElementById('edit-match-number').value = match.match_number;
        document.getElementById('edit-match-type').value = match.match_type;
        document.getElementById('edit-red-team1').value = match.red_team1 ? match.red_team1.number : '';
        document.getElementById('edit-red-team2').value = match.red_team2 ? match.red_team2.number : '';
        document.getElementById('edit-blue-team1').value = match.blue_team1 ? match.blue_team1.number : '';
        document.getElementById('edit-blue-team2').value = match.blue_team2 ? match.blue_team2.number : '';
        document.getElementById('edit-red-score').value = match.red_score;
        document.getElementById('edit-blue-score').value = match.blue_score;
        document.getElementById('edit-match-status').value = match.status;
        
        openModal('edit-match-modal');
    } catch (error) {
        console.error('Error loading match:', error);
        showToast('Error loading match', 'error');
    }
}

async function saveMatch() {
    const matchId = document.getElementById('edit-match-id').value;
    const data = {
        match_number: parseInt(document.getElementById('edit-match-number').value),
        match_type: document.getElementById('edit-match-type').value,
        red_team1: document.getElementById('edit-red-team1').value,
        red_team2: document.getElementById('edit-red-team2').value,
        blue_team1: document.getElementById('edit-blue-team1').value,
        blue_team2: document.getElementById('edit-blue-team2').value,
        red_score: parseInt(document.getElementById('edit-red-score').value),
        blue_score: parseInt(document.getElementById('edit-blue-score').value),
        status: document.getElementById('edit-match-status').value
    };
    
    try {
        const response = await fetch(`/api/admin/matches/${matchId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Match updated successfully!', 'success');
            closeModal('edit-match-modal');
            loadMatches();
        } else {
            showToast(result.error || 'Error updating match', 'error');
        }
    } catch (error) {
        console.error('Error saving match:', error);
        showToast('Error saving match', 'error');
    }
}

async function deleteMatch(matchId) {
    if (!confirm('Are you sure you want to delete this match? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/matches/${matchId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Match deleted successfully', 'success');
            loadMatches();
        } else {
            const result = await response.json();
            showToast(result.error || 'Error deleting match', 'error');
        }
    } catch (error) {
        console.error('Error deleting match:', error);
        showToast('Error deleting match', 'error');
    }
}

async function deleteAllMatches() {
    if (!confirm('Are you sure you want to DELETE ALL MATCHES? This cannot be undone!')) {
        return;
    }
    
    if (!confirm('This will permanently delete all match data. Are you ABSOLUTELY sure?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/admin/matches/all', {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('All matches deleted', 'success');
            loadMatches();
        } else {
            showToast(result.error || 'Error deleting matches', 'error');
        }
    } catch (error) {
        console.error('Error deleting matches:', error);
        showToast('Error deleting matches', 'error');
    }
}

// TEAMS FUNCTIONS
async function loadTeams() {
    try {
        const response = await fetch('/api/teams');
        const teams = await response.json();
        
        const tbody = document.getElementById('teams-tbody');
        
        if (teams.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="no-data">No teams found</td></tr>';
            return;
        }
        
        tbody.innerHTML = '';
        teams.forEach(team => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${team.id}</td>
                <td><span class="badge badge-blue">${team.number}</span></td>
                <td>${team.name}</td>
                <td class="action-buttons">
                    <button class="btn btn-danger btn-sm" onclick="deleteTeam(${team.id}, '${team.number}')">Delete</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading teams:', error);
        showToast('Error loading teams', 'error');
    }
}

async function deleteTeam(teamId, teamNumber) {
    if (!confirm(`Are you sure you want to delete Team ${teamNumber}? This cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/teams/${teamId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Team deleted successfully', 'success');
            loadTeams();
        } else {
            showToast(result.error || 'Error deleting team', 'error');
        }
    } catch (error) {
        console.error('Error deleting team:', error);
        showToast('Error deleting team', 'error');
    }
}

// RANKINGS FUNCTIONS
async function loadRankings() {
    try {
        const response = await fetch('/api/rankings');
        const rankings = await response.json();
        
        const tbody = document.getElementById('rankings-tbody');
        
        if (rankings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="no-data">No rankings found</td></tr>';
            return;
        }
        
        tbody.innerHTML = '';
        rankings.forEach(ranking => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="badge badge-success">#${ranking.rank}</span></td>
                <td><span class="badge badge-blue">${ranking.team_number}</span></td>
                <td>${ranking.team_name}</td>
                <td><strong>${ranking.ranking_points}</strong></td>
                <td>${ranking.rank_change}</td>
                <td class="action-buttons">
                    <button class="btn btn-primary btn-sm" onclick="editRanking(${ranking.team_number})">Edit</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading rankings:', error);
        showToast('Error loading rankings', 'error');
    }
}

async function editRanking(teamNumber) {
    try {
        const response = await fetch('/api/rankings');
        const rankings = await response.json();
        const ranking = rankings.find(r => r.team_number === teamNumber);
        
        if (!ranking) {
            showToast('Ranking not found', 'error');
            return;
        }
        
        document.getElementById('edit-ranking-id').value = teamNumber;
        document.getElementById('edit-ranking-team').value = `${ranking.team_number} - ${ranking.team_name}`;
        document.getElementById('edit-ranking-points').value = ranking.ranking_points;
        
        openModal('edit-ranking-modal');
    } catch (error) {
        console.error('Error loading ranking:', error);
        showToast('Error loading ranking', 'error');
    }
}

async function saveRanking() {
    const teamNumber = document.getElementById('edit-ranking-id').value;
    const rankingPoints = parseInt(document.getElementById('edit-ranking-points').value);
    
    try {
        const response = await fetch(`/api/admin/rankings/${teamNumber}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ranking_points: rankingPoints })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Ranking updated successfully!', 'success');
            closeModal('edit-ranking-modal');
            loadRankings();
        } else {
            showToast(result.error || 'Error updating ranking', 'error');
        }
    } catch (error) {
        console.error('Error saving ranking:', error);
        showToast('Error saving ranking', 'error');
    }
}

async function resetAllRankings() {
    if (!confirm('Are you sure you want to RESET ALL RANKINGS? All teams will go back to 0 points!')) {
        return;
    }
    
    try {
        const response = await fetch('/api/admin/rankings/reset', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('All rankings reset to 0', 'success');
            loadRankings();
        } else {
            showToast(result.error || 'Error resetting rankings', 'error');
        }
    } catch (error) {
        console.error('Error resetting rankings:', error);
        showToast('Error resetting rankings', 'error');
    }
}

// MATCH EVENTS FUNCTIONS
async function loadMatchEvents() {
    const filterMatchId = document.getElementById('event-filter-match').value;
    
    try {
        let url = '/api/admin/events';
        if (filterMatchId) {
            url += `?match_id=${filterMatchId}`;
        }
        
        const response = await fetch(url);
        const events = await response.json();
        
        const tbody = document.getElementById('events-tbody');
        
        if (events.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="no-data">No events found</td></tr>';
            return;
        }
        
        tbody.innerHTML = '';
        events.forEach(event => {
            const row = document.createElement('tr');
            const timestamp = event.timestamp ? new Date(event.timestamp).toLocaleString() : 'N/A';
            row.innerHTML = `
                <td>${event.id}</td>
                <td>${event.match_id}</td>
                <td><span class="badge badge-${event.alliance === 'red' ? 'red' : 'blue'}">${event.alliance}</span></td>
                <td>${event.event_type}</td>
                <td>${event.points}</td>
                <td>${timestamp}</td>
                <td class="action-buttons">
                    <button class="btn btn-danger btn-sm" onclick="deleteEvent(${event.id})">Delete</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading events:', error);
        showToast('Error loading events', 'error');
    }
}

async function deleteEvent(eventId) {
    if (!confirm('Are you sure you want to delete this event?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/events/${eventId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Event deleted successfully', 'success');
            loadMatchEvents();
        } else {
            showToast(result.error || 'Error deleting event', 'error');
        }
    } catch (error) {
        console.error('Error deleting event:', error);
        showToast('Error deleting event', 'error');
    }
}

// Initial load
loadMatches();

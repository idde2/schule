const socket = io();

let state = { players: [], matches: [] };

socket.on("state_update", s => {
    state = s;
    renderPlayers();
    renderMatches();
});

socket.on("connect", () => {
    socket.emit("request_state");
});

function initTournament() {
    fetch("/turnier/init", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            num_players: document.getElementById("num_players").value,
            max_parallel_games: document.getElementById("max_parallel_games").value
        })
    });
}

function startMatches() {
    fetch("/turnier/start", { method: "POST" });
}

function cooldownTick() {
    fetch("/turnier/cooldown", { method: "POST" });
}

function reportResult(matchId, winnerId) {
    fetch("/turnier/result", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ match_id: matchId, winner_id: winnerId })
    });
}

function renderPlayers() {
    const div = document.getElementById("players");
    div.innerHTML = "";
    state.players.forEach(p => {
        div.innerHTML += `<div class="player">${p.name} — ${p.status}</div>`;
    });
}

function renderMatches() {
    const div = document.getElementById("matches");
    div.innerHTML = "";
    state.matches.forEach(m => {
        let html = `<div class="match">
            Match ${m.id}: Spieler ${m.p1} vs Spieler ${m.p2}<br>
            Status: ${m.status}<br>`;

        if (m.status === "playing") {
            html += `
                <button onclick="reportResult(${m.id}, ${m.p1})">Spieler ${m.p1} gewinnt</button>
                <button onclick="reportResult(${m.id}, ${m.p2})">Spieler ${m.p2} gewinnt</button>
            `;
        }

        if (m.status === "finished") {
            html += `Sieger: Spieler ${m.winner}`;
        }

        html += `</div>`;
        div.innerHTML += html;
    });
}

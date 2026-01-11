const s = document.getElementById("search");
s.oninput = () => {
    const v = s.value.toLowerCase();
    document.querySelectorAll("table tr").forEach(r => {
        const t = r.textContent.toLowerCase();
        r.style.display = t.includes(v) ? "" : "none";
    });
};

const sidebar = document.getElementById("sidebar");
document.getElementById("toggleBtn").onclick = () =>
    sidebar.classList.toggle("open");

const socket = io();

socket.on("tabelle_update", (data) => {
    const tbody = document.getElementById("tbody");
    if (!tbody) return;

    tbody.innerHTML = "";
    data.daten.forEach(row => {
        tbody.innerHTML += `
            <tr>
                <td>${row.id}</td>
                <td>${row.name}</td>
                <td>${row.wert}</td>
            </tr>
        `;
    });
});

function applyTheme(theme) {
    document.body.classList.toggle("light", theme === "light");
    document.getElementById("themeToggle").textContent = theme === "light" ? "☀️" : "🌙";
}

let savedTheme = localStorage.getItem("theme") ||
    (window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");

applyTheme(savedTheme);

document.getElementById("themeToggle").onclick = () => {
    const btn = document.getElementById("themeToggle");
    btn.classList.add("rotate");

    setTimeout(() => btn.classList.remove("rotate"), 400);

    const newTheme = document.body.classList.contains("light") ? "dark" : "light";
    applyTheme(newTheme);
    localStorage.setItem("theme", newTheme);
};



let touchStartX = 0;

document.addEventListener("touchstart", (e) => {
    touchStartX = e.touches[0].clientX;
});

document.addEventListener("touchend", (e) => {
    const touchEndX = e.changedTouches[0].clientX;
    const diff = touchEndX - touchStartX;

    if (diff > 80) {
        sidebar.classList.add("open");
    }
    if (diff < -80) {
        sidebar.classList.remove("open");
    }
});

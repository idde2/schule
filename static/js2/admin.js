const sidebar = document.getElementById("sidebar");
document.getElementById("toggleBtn").onclick = () =>
    sidebar.classList.toggle("open");

const socket = io();

socket.on("admin_update", (data) => {
    const tbody = document.getElementById("tbody");
    const mobile = document.getElementById("mobileCards");

    tbody.innerHTML = `
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Wert</th>
            <th>Aktionen</th>
        </tr>
    `;

    mobile.innerHTML = "";

    data.daten.forEach(row => {
        tbody.innerHTML += `
            <tr>
                <td>${row.id}</td>
                <td>${row.name}</td>
                <td>${row.wert}</td>
                <td>
                    <a href="/edit/${row.id}">Bearbeiten</a> |
                    <a href="/delete/${row.id}" class="delete">Löschen</a>
                </td>
            </tr>
        `;

        mobile.innerHTML += `
            <div class="card">
                <strong>${row.name}</strong><br>
                ID: ${row.id}<br>
                Wert: ${row.wert}<br><br>
                <a href="/edit/${row.id}">Bearbeiten</a> |
                <a href="/delete/${row.id}" class="delete">Löschen</a>
            </div>
        `;
    });
});

function applyTheme(theme) {
    document.body.classList.toggle("light", theme === "light");
    document.getElementById("themeToggle").textContent =
        theme === "light" ? "☀️" : "🌙";

    const logoutIcon = document.getElementById("logoutIcon");
    logoutIcon.src = theme === "light"
        ? "/static/images/logout_dark.png"
        : "/static/images/logout_light.png";
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
    const diff = e.changedTouches[0].clientX - touchStartX;
    if (diff > 80) sidebar.classList.add("open");
    if (diff < -80) sidebar.classList.remove("open");
});
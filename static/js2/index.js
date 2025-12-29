const sidebar = document.getElementById("sidebar");
document.getElementById("toggleBtn").onclick = () =>
    sidebar.classList.toggle("open");

const socket = io();

socket.on("live_update", (data) => {
    const list = document.getElementById("liveCards");
    list.innerHTML = "";

    data.forEach(item => {
        list.innerHTML += `
            <div class="card">
                <strong>${item.name}</strong><br>
                Wert: ${item.wert}
            </div>
        `;
    });

    if (data.length > 0) {
        document.getElementById("id").textContent = data[0].id;
        document.getElementById("name").textContent = data[0].name;
        document.getElementById("wert").textContent = data[0].wert;
    }
});

function applyTheme(theme) {
    document.body.classList.toggle("light", theme === "light");
    document.getElementById("themeToggle").textContent =
        theme === "light" ? "☀️" : "🌙";
}

let savedTheme = localStorage.getItem("theme") ||
    (window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");

applyTheme(savedTheme);

document.getElementById("themeToggle").onclick = () => {
    const btn = document.getElementById("themeToggle");
    btn.classList.add("rotate");

    setTimeout(() => btn.classList.remove("rotate"), 400);

    const newTheme =
        document.body.classList.contains("light") ? "dark" : "light";

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

    if (diff > 80) sidebar.classList.add("open");
    if (diff < -80) sidebar.classList.remove("open");
});
const sidebar = document.getElementById("sidebar");
document.getElementById("toggleBtn").onclick = () =>
    sidebar.classList.toggle("open");

const socket = io();

socket.on("disconnect", () => {
    document.getElementById("reconnect").style.display = "block";
});

socket.on("connect", () => {
    document.getElementById("reconnect").style.display = "none";
});

socket.on("update", (data) => {
    const idEl = document.getElementById("id");
    const nameEl = document.getElementById("name");
    const wertEl = document.getElementById("wert");

    idEl.textContent = data.id ?? "–";
    nameEl.textContent = data.name ?? "–";

    const old = parseFloat(wertEl.textContent) || 0;
    const target = data.wert ?? 0;
    const duration = 300;
    const start = performance.now();
    function animate(t){
        const p = Math.min((t - start) / duration, 1);
        wertEl.textContent = (old + (target - old) * p).toFixed(2);
        if(p < 1) requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);

    const list = document.getElementById("liveCards");
    list.innerHTML = "";
    if (data.name !== undefined) {
        list.innerHTML = `
            <div class="card">
                <strong>${data.name}</strong><br>
                Wert: ${data.wert}
            </div>
        `;
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
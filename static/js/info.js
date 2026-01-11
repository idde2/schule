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

document.getElementById("toggleBtn").onclick = () =>
    document.getElementById("sidebar").classList.toggle("open");

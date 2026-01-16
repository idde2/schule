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

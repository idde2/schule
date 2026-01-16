


const f = document.getElementById("filter");
f.onchange = () => {
    const v = f.value.toLowerCase();
    document.querySelectorAll(".card").forEach(c => {
        const t = c.textContent.toLowerCase();
        c.style.display = v === "" || t.includes(v) ? "" : "none";
    });
};

document.getElementById("deleteLogsBtn").onclick = () => {
    const pin = prompt("PIN eingeben:");
    if (pin === "1234") {
        window.location.href = "/delete_all_logs";
    } else if (pin !== null) {
        alert("Falscher PIN");
    }
};


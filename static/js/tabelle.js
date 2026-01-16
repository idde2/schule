const s = document.getElementById("search");
s.oninput = () => {
    const v = s.value.toLowerCase();
    document.querySelectorAll("table tr").forEach(r => {
        const t = r.textContent.toLowerCase();
        r.style.display = t.includes(v) ? "" : "none";
    });
};


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


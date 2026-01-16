const s = document.getElementById("search");
s.oninput = () => {
    const v = s.value.toLowerCase();
    document.querySelectorAll("table tr").forEach(r => {
        const t = r.textContent.toLowerCase();
        r.style.display = t.includes(v) ? "" : "none";
    });
};


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
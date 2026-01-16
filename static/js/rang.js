

function konfetti() {
    for (let i = 0; i < 80; i++) {
        const d = document.createElement("div");
        d.style.position = "fixed";
        d.style.width = "8px";
        d.style.height = "8px";
        d.style.background = `hsl(${Math.random()*360}, 100%, 50%)`;
        d.style.left = Math.random()*100 + "vw";
        d.style.top = "-20px";
        d.style.opacity = 1;
        d.style.transition = "transform 1.5s ease-out, opacity 1.5s ease-out";
        document.body.appendChild(d);
        setTimeout(() => {
            d.style.transform = `translateY(${100 + Math.random()*50}vh) rotate(${Math.random()*360}deg)`;
            d.style.opacity = 0;
        }, 10);
        setTimeout(() => d.remove(), 1600);
    }
}

const socket = io();
let lastFirst = "";

socket.on("rang_update", (data) => {
    const tbody = document.getElementById("tbody");
    const mobile = document.getElementById("mobileCards");

    mobile.innerHTML = "";
    data.daten.forEach(r => {
        mobile.innerHTML += `
            <div class="card">
                <strong>${r.name}</strong><br>
                ${r.wert}
            </div>
        `;
    });

    let rows = Array.from(tbody.querySelectorAll("tr"));
    const names = rows.map(r => r.children[0].textContent);

    data.daten.forEach(row => {
        if (!names.includes(row.name)) {
            const tr = document.createElement("tr");
            tr.innerHTML = `<td>${row.name}</td><td>${row.wert}</td>`;
            tbody.appendChild(tr);
        }
    });

    rows = Array.from(tbody.querySelectorAll("tr"));
    const oldPos = new Map();
    rows.forEach(tr => oldPos.set(tr.children[0].textContent, tr.getBoundingClientRect()));

    data.daten.forEach(row => {
        const tr = rows.find(r => r.children[0].textContent === row.name);
        if (tr) {
            const old = Number(tr.children[1].textContent);
            const neu = Number(row.wert);
            if (neu > old) tr.classList.add("glow-up");
            if (neu < old) tr.classList.add("glow-down");
            tr.children[1].textContent = neu;
            setTimeout(() => tr.classList.remove("glow-up", "glow-down"), 1000);
        }
    });

    const sorted = [...data.daten].sort((a,b)=>b.wert - a.wert);
    const newOrder = sorted.map(r => rows.find(tr => tr.children[0].textContent === r.name));

    if (sorted[0].name !== lastFirst) {
        konfetti();
        lastFirst = sorted[0].name;
    }

    newOrder.forEach((tr, i) => {
        tr.classList.remove("top1","top2","top3");
        if (i===0) tr.classList.add("top1");
        if (i===1) tr.classList.add("top2");
        if (i===2) tr.classList.add("top3");
    });

    newOrder.forEach(tr => tbody.appendChild(tr));

    newOrder.forEach(tr => {
        const name = tr.children[0].textContent;
        const old = oldPos.get(name);
        const neu = tr.getBoundingClientRect();
        const dy = old.top - neu.top;
        if (Math.abs(dy) > 3) {
            tr.style.transition = "none";
            tr.style.transform = `translateY(${dy}px)`;
            requestAnimationFrame(() => {
                tr.style.transition = "transform 0.6s cubic-bezier(.34,1.56,.64,1)";
                tr.style.transform = "translateY(0)";
            });
        }
    });
});


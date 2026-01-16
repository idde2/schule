document.querySelector("form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    const response = await fetch("/eingabe", {
        method: "POST",
        body: formData
    });

    let result = null;
    try {
        result = await response.json();
    } catch {
        alert("Fehler: Server hat keine gültige Antwort gesendet.");
        return;
    }

    if (!result.success) {
        alert("Fehler beim Speichern");
        return;
    }

    form.reset();
});


const raw = document.getElementById("namenData").textContent;
const existingNames = JSON.parse(raw);


document.getElementById("name").addEventListener("input", () => {
    const input = document.getElementById("name");
    const value = input.value.trim();
    input.style.border = existingNames.includes(value) ? "2px solid red" : "";
});



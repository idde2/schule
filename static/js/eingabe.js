document.addEventListener("DOMContentLoaded", () => {

    const pageData = document.getElementById("pageData");
    let currentTyp = pageData?.dataset.typ || "";


    const f = document.getElementById("input_typ");

    if (currentTyp) {
        f.value = currentTyp;
    }


    f.onchange = () => {
        const v = f.value.toLowerCase();
        window.location.href = "/eingabe/" + v;
    };


    document.querySelector("form").addEventListener("submit", async (e) => {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);

        if (!currentTyp) {
            currentTyp = f.value.toLowerCase();
        }

        const response = await fetch(`/eingabe/${currentTyp}`, {
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

        f.value = currentTyp;

        form.reset();
    });

    const raw = document.getElementById("namenData").textContent;
    const existingNames = JSON.parse(raw);

    document.getElementById("name").addEventListener("input", () => {
        const input = document.getElementById("name");
        const value = input.value.trim();
        input.style.border = existingNames.includes(value) ? "2px solid red" : "";
    });

});


console.log(daten);
const log = document.getElementById("cmd_log");
log.innerText = daten + "\n";

const input = document.getElementById("cmd");
input.focus();

document.getElementById("cmd").addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        window.location.href = "/cmd/" + encodeURIComponent(this.value);
        this.value = "";
    }
});

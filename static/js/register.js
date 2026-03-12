document.getElementById("regForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value;

    localStorage.setItem("savedEmail", email);

    window.location.href = "/register2/" + encodeURIComponent(email);
});

const saved = localStorage.getItem("savedEmail");
if (saved) {
    document.getElementById("email").value = saved;
}

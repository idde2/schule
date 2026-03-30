const f = document.getElementById("input_typ");
f.onchange = () => {
    const v = f.value.toLowerCase();
    window.location.href = "/rang/" + v
};
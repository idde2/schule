const windows_menu_btn = document.getElementById("windows_menu_btn");
const explorer_menu_btn = document.getElementById("explorer_menu_btn");
const word_menu_btn = document.getElementById("word_menu_btn");
const vsc_menu_btn = document.getElementById("vsc_menu_btn");
const whatsapp_menu_btn = document.getElementById("whatsapp_menu_btn");
const pfeil_menu_btn = document.getElementById("pfeil_menu_btn");
const lang_menu_btn = document.getElementById("lang_menu_btn");

const search = document.getElementById("search");
const search_text = document.getElementById("search_text");

const windows_menu = document.getElementById("windows_menu");
const explorer_menu = document.getElementById("explorer_menu");
const word_menu = document.getElementById("word_menu");
const vsc_menu = document.getElementById("vsc_menu");
const whatsapp_menu = document.getElementById("whatsapp_menu");
const pfeil_menu = document.getElementById("pfeil_menu");
const lang_menu = document.getElementById("lang_menu");
const search_menu = document.getElementById("search_menu");

function makeDraggable(win) {
    let isDragging = false;
    let offsetX = 0;
    let offsetY = 0;

    const dragArea = win.querySelector(".titlebar") || win;

    dragArea.addEventListener("mousedown", (e) => {
        isDragging = true;
        offsetX = e.clientX - win.offsetLeft;
        offsetY = e.clientY - win.offsetTop;
        dragArea.style.cursor = "grabbing";
    });

    document.addEventListener("mousemove", (e) => {
        if (!isDragging) return;

        win.style.left = (e.clientX - offsetX) + "px";
        win.style.top  = (e.clientY - offsetY) + "px";
    });

    document.addEventListener("mouseup", () => {
        isDragging = false;
        dragArea.style.cursor = "grab";
    });
}


function update() {
  search_menu.style.display = search_s ? "none" : "block";
  search_menu.style.display = search_s ? "none" : "block";
}
function toggleMenu(menu) {
    if (menu.classList.contains("active")) {
        // Menü schließen
        menu.classList.add("closing");
        setTimeout(() => {
            menu.classList.remove("active");
            menu.classList.remove("closing");
        }, 300); // Dauer der gone-Animation
    } else {
        // Menü öffnen
        menu.classList.add("active");
    }
}

windows_menu_btn.addEventListener("click", () => toggleMenu(windows_menu));
explorer_menu_btn.addEventListener("click", () => toggleMenu(explorer_menu));
word_menu_btn.addEventListener("click", () => toggleMenu(word_menu));
vsc_menu_btn.addEventListener("click", () => toggleMenu(vsc_menu));
whatsapp_menu_btn.addEventListener("click", () => toggleMenu(whatsapp_menu));
pfeil_menu_btn.addEventListener("click", () => toggleMenu(pfeil_menu));
lang_menu_btn.addEventListener("click", () => toggleMenu(lang_menu));

makeDraggable(explorer_menu);
makeDraggable(word_menu);
makeDraggable(vsc_menu);
makeDraggable(whatsapp_menu);
makeDraggable(pfeil_menu);
makeDraggable(lang_menu);





search.addEventListener("focus", function () { search_s = false; update();  });
search.addEventListener("blur", function () { search_s = true;   update();  });
search.oninput = () => { search_text.innerText = search.value;}



const time = document.getElementById("time")
const date = document.getElementById("date")


setInterval(() => {
    time.innerText = new Date().toLocaleTimeString("de-DE", { timeStyle: "short" });
    date.innerText = new Date().toLocaleDateString("de-DE", { dateStyle: "medium" });
}, 1000);

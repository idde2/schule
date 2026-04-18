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




let windows_menu_btn_s = true;
let search_s = true;
let explorer_menu_btn_s = true;
let word_menu_btn_s = true;
let vsc_menu_btn_s = true;
let whatsapp_menu_btn_s = true;
let pfeil_menu_btn_s = true;
let lang_menu_btn_s = true;

function update() {
    windows_menu.style.display = windows_menu_btn_s ? "none" : "block";
    explorer_menu.style.display = explorer_menu_btn_s ? "none" : "flex";
    word_menu.style.display = word_menu_btn_s ? "none" : "block";
    vsc_menu.style.display = vsc_menu_btn_s ? "none" : "block";
    whatsapp_menu.style.display = whatsapp_menu_btn_s ? "none" : "block";
    pfeil_menu.style.display = pfeil_menu_btn_s ? "none" : "block";
    lang_menu.style.display = lang_menu_btn_s ? "none" : "block";

    search_menu.style.display = search_s ? "none" : "block";
    search_menu.style.display = search_s ? "none" : "block";
}


windows_menu_btn.addEventListener("click", function() { windows_menu_btn_s = !windows_menu_btn_s;      update(); });
explorer_menu_btn.addEventListener("click", function(){ explorer_menu_btn_s = !explorer_menu_btn_s;    update(); });
word_menu_btn.addEventListener("click", function ()  { word_menu_btn_s = !word_menu_btn_s;             update(); });
vsc_menu_btn.addEventListener("click", function () { vsc_menu_btn_s = !vsc_menu_btn_s;                 update(); });
whatsapp_menu_btn.addEventListener("click", function (){ whatsapp_menu_btn_s = ! whatsapp_menu_btn_s;  update(); });
pfeil_menu_btn.addEventListener("click", function () { pfeil_menu_btn_s = !pfeil_menu_btn_s;           update(); });
lang_menu_btn.addEventListener("click",function () { lang_menu_btn_s = !lang_menu_btn_s;               update(); });

search.addEventListener("focus", function () { search_s = false;                                       update();  });
search.addEventListener("blur", function () { search_s = true;                                         update();  });
search.oninput = () => { search_text.innerText = search.value;}





const time = document.getElementById("time")
const date = document.getElementById("date")


setInterval(() => {
    time.innerText = new Date().toLocaleTimeString("de-DE", { timeStyle: "short" });
    date.innerText = new Date().toLocaleDateString("de-DE", { dateStyle: "medium" });
}, 1000);
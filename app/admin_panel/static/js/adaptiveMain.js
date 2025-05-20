function hideSidebarOnMobile() {
  if (window.innerWidth < 600) {
    document.getElementById("sidebar").classList.add("d-none");
    document.getElementById("content").classList.remove("d-none");
  }
}

function showSidebar() {
  document.getElementById("sidebar").classList.remove("d-none");
  document.getElementById("content").classList.add("d-none");
}

function resetLayoutOnWideScreen() {
  if (window.innerWidth >= 600) {
    // Убираем d-none независимо от состояния
    document.getElementById("sidebar").classList.remove("d-none");
    document.getElementById("content").classList.remove("d-none");
  }
}
console.log("Hello");
if (window.innerWidth < 600) {
  window.selected ? hideSidebarOnMobile() : showSidebar();
}
window.addEventListener("resize", () => {
  resetLayoutOnWideScreen();
});

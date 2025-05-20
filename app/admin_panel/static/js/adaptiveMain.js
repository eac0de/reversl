function resetLayoutOnWideScreen() {
  if (window.innerWidth >= 600) {
    document.getElementById("sidebar").classList.remove("d-none");
    document.getElementById("content").classList.remove("d-none");
  }
}
if (window.innerWidth < 600) {
  document.getElementById("sidebar").classList.add("d-none");
}
window.addEventListener("resize", () => {
  if (window.innerWidth > 600) {
    resetLayoutOnWideScreen();
  }
});

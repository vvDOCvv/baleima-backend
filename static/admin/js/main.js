const $btnNav = document.getElementById("toggle-nav-sidebar");
const $main = document.getElementById("main");
const $nav = document.getElementById("nav-sidebar");

$btnNav.addEventListener("click", () => {
  $main.classList.toggle("shifted");

  const currentAtriaExpand = $nav.getAttribute("aria-expanded");
  const newAriaExpand = currentAtriaExpand === "True" ? "False" : "True";

  $nav.setAttribute("aria-expanded", newAriaExpand);
});

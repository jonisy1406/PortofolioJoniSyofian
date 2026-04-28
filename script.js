function scrollToContact(){
  document.getElementById("contact").scrollIntoView({behavior:"smooth"});
}

const header = document.querySelector("header");
const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector("#site-nav");
const revealElements = document.querySelectorAll(".reveal");

function updateHeader(){
  header.classList.toggle("scrolled", window.scrollY > 16);
}

function closeMenu(){
  header.classList.remove("nav-open");
  menuToggle?.setAttribute("aria-expanded", "false");
  menuToggle?.setAttribute("aria-label", "Open navigation menu");
  const icon = menuToggle?.querySelector("i");
  icon?.classList.remove("fa-xmark");
  icon?.classList.add("fa-bars");
}

function toggleMenu(){
  const isOpen = header.classList.toggle("nav-open");
  menuToggle?.setAttribute("aria-expanded", String(isOpen));
  menuToggle?.setAttribute("aria-label", isOpen ? "Close navigation menu" : "Open navigation menu");
  const icon = menuToggle?.querySelector("i");
  icon?.classList.toggle("fa-bars", !isOpen);
  icon?.classList.toggle("fa-xmark", isOpen);
}

revealElements.forEach((element, index) => {
  element.style.setProperty("--delay", `${Math.min(index * 80, 320)}ms`);
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("active");
      observer.unobserve(entry.target);
    }
  });
}, {
  threshold: 0.15,
  rootMargin: "0px 0px -60px 0px"
});

revealElements.forEach((element) => observer.observe(element));
window.addEventListener("scroll", updateHeader, {passive:true});
menuToggle?.addEventListener("click", toggleMenu);
siteNav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeMenu();
});
document.addEventListener("click", (event) => {
  if (!header.contains(event.target)) closeMenu();
});
window.addEventListener("resize", () => {
  if (window.innerWidth > 900) closeMenu();
});
updateHeader();

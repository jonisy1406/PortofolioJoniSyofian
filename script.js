function scrollToContact(){
  document.getElementById("contact").scrollIntoView({behavior:"smooth"});
}

const header = document.querySelector("header");
const revealElements = document.querySelectorAll(".reveal");

function updateHeader(){
  header.classList.toggle("scrolled", window.scrollY > 16);
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
updateHeader();

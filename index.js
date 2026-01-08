// Sticky nav & section highlighting
document.addEventListener("DOMContentLoaded", () => {
  const sections = document.querySelectorAll("main section");
  const navLinks = document.querySelectorAll(".nav-links a");

  function activateNav() {
    let index = sections.length;

    while(--index && window.scrollY + 100 < sections[index].offsetTop) {}
    
    navLinks.forEach((link) => link.classList.remove("active"));
    navLinks[index].classList.add("active");
  }

  activateNav();
  window.addEventListener("scroll", activateNav);

  // Smooth scrolling
  navLinks.forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute("href"));
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  // Simple fade-in on scroll
  const faders = document.querySelectorAll(".hero, section");
  const options = { threshold: 0.1 };
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if(entry.isIntersecting){
        entry.target.classList.add("fade-in");
        observer.unobserve(entry.target);
      }
    });
  }, options);

  faders.forEach(fader => observer.observe(fader));
});

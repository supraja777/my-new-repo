document.addEventListener("DOMContentLoaded", () => {
  // Sticky nav highlight
  const sections = document.querySelectorAll("main section");
  const navLinks = document.querySelectorAll(".nav-links a");

  function activateNav() {
    let index = sections.length;
    while (--index && window.scrollY + 150 < sections[index].offsetTop) {}
    navLinks.forEach(link => link.classList.remove("active"));
    navLinks[index].classList.add("active");
  }

  activateNav();
  window.addEventListener("scroll", activateNav);

  // Smooth scrolling
  navLinks.forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      document.querySelector(link.getAttribute("href")).scrollIntoView({behavior: "smooth"});
    });
  });

  // Fade-in sections
  const faders = document.querySelectorAll("section, .hero");
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if(entry.isIntersecting){
        entry.target.classList.add("visible");
        obs.unobserve(entry.target);
      }
    });
  }, {threshold: 0.1});

  faders.forEach(fader => observer.observe(fader));
});

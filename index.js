document.addEventListener("DOMContentLoaded", () => {
  const sections = document.querySelectorAll("section");
  const navLinks = document.querySelectorAll("nav a");

  // Smooth scroll
  navLinks.forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      document.querySelector(link.getAttribute("href"))
        .scrollIntoView({ behavior: "smooth" });
    });
  });

  // Intersection fade
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate-fadeIn");
      }
    });
  }, { threshold: 0.15 });

  sections.forEach(s => observer.observe(s));

  // Active nav highlight
  window.addEventListener("scroll", () => {
    let current = "";
    sections.forEach(section => {
      if (pageYOffset >= section.offsetTop - 140) {
        current = section.id;
      }
    });

    navLinks.forEach(a => a.classList.remove("active"));
    const active = document.querySelector(`nav a[href="#${current}"]`);
    if (active) active.classList.add("active");
  });
});

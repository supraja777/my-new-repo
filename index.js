document.addEventListener("DOMContentLoaded", () => {
  const navLinks = document.querySelectorAll(".nav-links a");

  navLinks.forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      document.querySelector(link.getAttribute("href")).scrollIntoView({
        behavior: "smooth"
      });
    });
  });

  const sections = document.querySelectorAll("section[id]");
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        history.replaceState(null, null, "#" + entry.target.id);
        navLinks.forEach(a => a.classList.remove("active"));
        document.querySelector(`.nav-links a[href="#${entry.target.id}"]`).classList.add("active");
      }
    });
  }, { threshold: 0.3 });

  sections.forEach(section => observer.observe(section));
});

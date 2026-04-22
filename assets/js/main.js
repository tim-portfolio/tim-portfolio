document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const nav = document.querySelector(".site-nav");
  const toggle = document.querySelector(".nav-toggle");
  const panel = document.querySelector(".nav-panel");
  const navLinks = Array.from(document.querySelectorAll('.nav-links a[href^="#"]'));
  const sections = Array.from(document.querySelectorAll("section[id]"));

  const closeMenu = () => {
    if (!toggle || !panel) return;
    toggle.setAttribute("aria-expanded", "false");
    panel.classList.remove("open");
    body.classList.remove("nav-open");
  };

  const openMenu = () => {
    if (!toggle || !panel) return;
    toggle.setAttribute("aria-expanded", "true");
    panel.classList.add("open");
    body.classList.add("nav-open");
  };

  if (toggle && panel) {
    toggle.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      if (expanded) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    document.addEventListener("click", (event) => {
      if (!panel.classList.contains("open")) return;
      const target = event.target;
      if (!(target instanceof Node)) return;
      if (panel.contains(target) || toggle.contains(target)) return;
      closeMenu();
    });
  }

  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      if (window.innerWidth <= 760) {
        closeMenu();
      }
    });
  });

  const setActiveLink = (id) => {
    navLinks.forEach((link) => {
      const isActive = link.getAttribute("href") === `#${id}`;
      link.classList.toggle("active", isActive);
    });
  };

  if ("IntersectionObserver" in window && sections.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveLink(entry.target.id);
          }
        });
      },
      {
        rootMargin: "-35% 0px -55% 0px",
        threshold: 0.05,
      }
    );

    sections.forEach((section) => observer.observe(section));
  } else if (sections[0]) {
    setActiveLink(sections[0].id);
  }

  const syncNavState = () => {
    if (!nav) return;
    nav.classList.toggle("is-scrolled", window.scrollY > 10);

    if (window.innerWidth > 760) {
      closeMenu();
    }
  };

  syncNavState();
  window.addEventListener("scroll", syncNavState, { passive: true });
  window.addEventListener("resize", syncNavState);
});

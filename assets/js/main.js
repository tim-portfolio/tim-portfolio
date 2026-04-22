document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const nav = document.querySelector(".site-nav");
  const toggle = document.querySelector(".nav-toggle");
  const panel = document.querySelector(".nav-panel");
  const navLinks = Array.from(document.querySelectorAll('.nav-links a[href^="#"]'));
  const sections = Array.from(document.querySelectorAll("section[id]"));
  const revealNodes = Array.from(document.querySelectorAll(".reveal"));
  const typewriterNodes = Array.from(document.querySelectorAll("[data-typewriter]"));
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!prefersReducedMotion) {
    body.classList.add("motion-ready");
  }

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

  const initializeTypewriter = (node) => {
    const originalText = (node.textContent || "").replace(/\s+/g, " ").trim();
    if (!originalText) return null;

    node.dataset.typeOriginal = originalText;
    node.textContent = "";
    node.setAttribute("aria-label", originalText);
    node.classList.add("typewriter-caret");

    return {
      node,
      text: originalText,
      speed: Number(node.dataset.typeSpeed || 26),
      delay: Number(node.dataset.typeDelay || 0),
      started: false,
    };
  };

  const typewriters = typewriterNodes
    .map(initializeTypewriter)
    .filter(Boolean);

  const finishTypewriter = (instance) => {
    instance.node.textContent = instance.text;
    instance.node.classList.remove("typewriter-caret");
    instance.started = true;
  };

  const runTypewriter = (instance) => {
    if (instance.started) return;
    instance.started = true;

    const { node, text, speed, delay } = instance;
    let index = 0;

    const step = () => {
      index += 1;
      node.textContent = text.slice(0, index);

      if (index < text.length) {
        window.setTimeout(step, speed);
      } else {
        window.setTimeout(() => {
          node.classList.remove("typewriter-caret");
        }, 350);
      }
    };

    window.setTimeout(step, delay);
  };

  if (prefersReducedMotion) {
    typewriters.forEach(finishTypewriter);
  }

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
    const navObserver = new IntersectionObserver(
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

    sections.forEach((section) => navObserver.observe(section));
  } else if (sections[0]) {
    setActiveLink(sections[0].id);
  }

  if (prefersReducedMotion) {
    revealNodes.forEach((node) => node.classList.add("is-visible"));
  } else if ("IntersectionObserver" in window && revealNodes.length) {
    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;

          entry.target.classList.add("is-visible");

          typewriters.forEach((instance) => {
            if (entry.target.contains(instance.node)) {
              runTypewriter(instance);
            }
          });

          observer.unobserve(entry.target);
        });
      },
      {
        rootMargin: "0px 0px -12% 0px",
        threshold: 0.14,
      }
    );

    revealNodes.forEach((node) => revealObserver.observe(node));
  } else {
    revealNodes.forEach((node) => node.classList.add("is-visible"));
    typewriters.forEach(runTypewriter);
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

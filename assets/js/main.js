document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const nav = document.querySelector(".site-nav");
  const toggle = document.querySelector(".nav-toggle");
  const panel = document.querySelector(".nav-panel");
  const navLinks = Array.from(document.querySelectorAll('.nav-links a[href^="#"]'));
  const sections = Array.from(document.querySelectorAll("section[id]"));
  const revealNodes = Array.from(document.querySelectorAll(".reveal"));
  const typewriterNodes = Array.from(document.querySelectorAll("[data-typewriter]"));
  const languageToggle = document.querySelector("[data-lang-toggle]");
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const i18n = window.PORTFOLIO_I18N || {};
  const zhTranslations = i18n.zh || {};
  const enTranslations = Object.fromEntries(
    Object.entries(zhTranslations).map(([english, chinese]) => [chinese, english])
  );
  const normalizeText = (value) => (value || "").replace(/\s+/g, " ").trim();
  const getStoredLanguage = () => {
    try {
      return window.localStorage.getItem("portfolio-language");
    } catch {
      return null;
    }
  };
  let currentLanguage = getStoredLanguage() === "zh" ? "zh" : "en";
  let typewriters = [];

  const translateValue = (value, language) => {
    const key = normalizeText(value);
    if (!key) return value;
    return language === "zh"
      ? (zhTranslations[key] || value)
      : (enTranslations[key] || value);
  };

  const setTextNodeValue = (node, value) => {
    const original = node.nodeValue || "";
    const leading = original.match(/^\s*/)?.[0] || "";
    const trailing = original.match(/\s*$/)?.[0] || "";
    node.nodeValue = `${leading}${value}${trailing}`;
  };

  const translateTextNodes = (language) => {
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode(node) {
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;
          if (parent.closest("script, style")) return NodeFilter.FILTER_REJECT;
          if (!normalizeText(node.nodeValue)) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        },
      }
    );

    const nodes = [];
    while (walker.nextNode()) {
      nodes.push(walker.currentNode);
    }

    nodes.forEach((node) => {
      const translated = translateValue(node.nodeValue, language);
      if (translated !== node.nodeValue) {
        setTextNodeValue(node, translated);
      }
    });
  };

  const updateLanguageControl = (language) => {
    if (!languageToggle) return;
    languageToggle.textContent = language === "zh" ? "EN" : "中文";
    languageToggle.setAttribute("aria-pressed", String(language === "zh"));
    languageToggle.setAttribute(
      "aria-label",
      language === "zh" ? "Switch to English" : "切换到中文"
    );
  };

  const cancelTypewriter = (instance) => {
    if (!instance) return;
    instance.timers.forEach((timer) => window.clearTimeout(timer));
    instance.timers = [];
    instance.started = true;
    instance.node.classList.remove("typewriter-caret");
  };

  const syncTypewritersToLanguage = (language) => {
    typewriters.forEach((instance) => {
      cancelTypewriter(instance);
      const translated = translateValue(instance.text || instance.node.textContent, language);
      instance.text = translated;
      instance.node.textContent = translated;
      instance.node.setAttribute("aria-label", translated);
    });
  };

  const applyLanguage = (language, options = {}) => {
    const nextLanguage = language === "zh" ? "zh" : "en";
    currentLanguage = nextLanguage;
    document.documentElement.lang = nextLanguage === "zh" ? "zh-Hans" : "en";
    document.title = i18n.title?.[nextLanguage] || document.title;
    const pageDescription = i18n.description?.[nextLanguage];
    if (pageDescription) {
      document.querySelector('meta[name="description"]')?.setAttribute("content", pageDescription);
    }

    if (typewriters.length) {
      syncTypewritersToLanguage(nextLanguage);
    }
    translateTextNodes(nextLanguage);
    updateLanguageControl(nextLanguage);

    if (options.persist !== false) {
      try {
        window.localStorage.setItem("portfolio-language", nextLanguage);
      } catch {
        // Ignore storage failures; language switching still works for the session.
      }
    }
  };

  if (!prefersReducedMotion) {
    body.classList.add("motion-ready");
  }

  applyLanguage(currentLanguage, { persist: false });

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
      timers: [],
    };
  };

  typewriters = typewriterNodes
    .map(initializeTypewriter)
    .filter(Boolean);

  const finishTypewriter = (instance) => {
    cancelTypewriter(instance);
    instance.node.textContent = instance.text;
    instance.node.classList.remove("typewriter-caret");
    instance.started = true;
  };

  const runTypewriter = (instance) => {
    if (instance.started) return;
    instance.started = true;

    const { node, text, speed, delay } = instance;
    let index = 0;

    const schedule = (callback, timeout) => {
      const timer = window.setTimeout(callback, timeout);
      instance.timers.push(timer);
    };

    const step = () => {
      index += 1;
      node.textContent = text.slice(0, index);

      if (index < text.length) {
        schedule(step, speed);
      } else {
        schedule(() => {
          node.classList.remove("typewriter-caret");
        }, 350);
      }
    };

    schedule(step, delay);
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

  if (languageToggle) {
    languageToggle.addEventListener("click", () => {
      applyLanguage(currentLanguage === "zh" ? "en" : "zh");
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
        threshold: 0.03,
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

/* ─────────────────────────────────────────
   LESTER PORTFOLIO — main.js
   ───────────────────────────────────────── */

"use strict";

// ── CUSTOM CURSOR ──────────────────────────
const cursor     = document.getElementById("cursor");
const cursorRing = document.getElementById("cursor-ring");

document.addEventListener("mousemove", (e) => {
  cursor.style.left     = e.clientX + "px";
  cursor.style.top      = e.clientY + "px";
  cursorRing.style.left = e.clientX + "px";
  cursorRing.style.top  = e.clientY + "px";
});

document.addEventListener("mousedown", () => {
  cursor.style.transform     = "translate(-50%, -50%) scale(0.7)";
  cursorRing.style.transform = "translate(-50%, -50%) scale(0.85)";
});

document.addEventListener("mouseup", () => {
  cursor.style.transform     = "translate(-50%, -50%) scale(1)";
  cursorRing.style.transform = "translate(-50%, -50%) scale(1)";
});

// ── SCROLL REVEAL ──────────────────────────
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12 }
);

document.querySelectorAll(".reveal").forEach((el) => revealObserver.observe(el));

// ── ACTIVE NAV LINK ON SCROLL ──────────────
const sections  = document.querySelectorAll("section[id]");
const navLinks  = document.querySelectorAll(".nav-links a");

const navObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        navLinks.forEach((a) => a.classList.remove("active"));
        const active = document.querySelector(`.nav-links a[href="#${entry.target.id}"]`);
        if (active) active.classList.add("active");
      }
    });
  },
  { threshold: 0.4 }
);

sections.forEach((s) => navObserver.observe(s));

// ── NAV SCROLL SHADOW ──────────────────────
const nav = document.querySelector("nav");

window.addEventListener("scroll", () => {
  if (window.scrollY > 40) {
    nav.style.boxShadow = "0 4px 40px rgba(0,0,0,0.6)";
  } else {
    nav.style.boxShadow = "none";
  }
});

// ── FOOTER YEAR ────────────────────────────
const footerYear = document.getElementById("footer-year");
if (footerYear) {
  footerYear.textContent = `© ${new Date().getFullYear()} Lester`;
}

// ── CONTACT FORM (sends to Python backend) ─
const contactForm = document.getElementById("contactForm");
const formStatus  = document.getElementById("formStatus");
const submitBtn   = document.getElementById("submitBtn");

if (contactForm) {
  contactForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      name:    document.getElementById("name").value.trim(),
      email:   document.getElementById("email").value.trim(),
      subject: document.getElementById("subject").value.trim(),
      message: document.getElementById("message").value.trim(),
    };

    submitBtn.textContent   = "Sending...";
    submitBtn.disabled      = true;
    formStatus.textContent  = "";
    formStatus.className    = "form-status";

    try {
      const res = await fetch("/api/contact", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok && data.success) {
        formStatus.textContent  = "✓ Message sent! I'll get back to you within 24 hours.";
        formStatus.classList.add("success");
        contactForm.reset();
      } else {
        throw new Error(data.message || "Server error");
      }
    } catch (err) {
      formStatus.textContent  = `✗ ${err.message || "Something went wrong. Please try again."}`;
      formStatus.classList.add("error");
    } finally {
      submitBtn.textContent = "Send Message";
      submitBtn.disabled    = false;
    }
  });
}

// ── SMOOTH PARALLAX ON HERO GLOWS ──────────
const heroGlow  = document.querySelector(".hero-glow");
const heroGlow2 = document.querySelector(".hero-glow2");

window.addEventListener("mousemove", (e) => {
  const xPct = (e.clientX / window.innerWidth  - 0.5) * 20;
  const yPct = (e.clientY / window.innerHeight - 0.5) * 20;

  if (heroGlow) {
    heroGlow.style.transform  = `translate(${xPct * 0.6}px, ${yPct * 0.6}px) scale(1)`;
  }
  if (heroGlow2) {
    heroGlow2.style.transform = `translate(${-xPct * 0.4}px, ${-yPct * 0.4}px) scale(1)`;
  }
});

// ── SKILL BAR ANIMATION ON REVEAL ──────────
// Re-trigger bar animation when skill cards come into view
const skillObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const bar = entry.target.querySelector(".skill-bar");
        if (bar) {
          bar.style.animation = "none";
          // Force reflow then re-apply animation
          void bar.offsetWidth;
          bar.style.animation = "";
        }
      }
    });
  },
  { threshold: 0.5 }
);

document.querySelectorAll(".skill-card").forEach((card) => skillObserver.observe(card));

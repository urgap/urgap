// urgap website — small progressive enhancements, no dependencies.
(() => {
  document.documentElement.classList.add("js");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---- top bar border + active nav link ----
  const topbar = document.querySelector(".topbar");
  const onScroll = () => topbar.classList.toggle("is-scrolled", window.scrollY > 8);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  const navLinks = [...document.querySelectorAll(".nav a[href^='#']:not(.nav__cta)")];
  const navTargets = navLinks.map((a) => document.querySelector(a.getAttribute("href"))).filter(Boolean);
  const navObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        navLinks.forEach((a) => a.classList.toggle("is-active", a.getAttribute("href") === `#${e.target.id}`));
      });
    },
    { rootMargin: "-45% 0px -50% 0px" }
  );
  navTargets.forEach((t) => navObserver.observe(t));

  // ---- reveal on scroll ----
  const revealables = document.querySelectorAll(".section__head, .split__text, .split__visual, .pac, .trio, .agent, .uri, .backends, .logos, .families, .install, .config");
  revealables.forEach((el) => el.classList.add("reveal"));
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("is-visible");
          revealObserver.unobserve(e.target);
        }
      });
    },
    { threshold: 0.12 }
  );
  revealables.forEach((el) => revealObserver.observe(el));

  // ---- Provenance-as-Code demo ----
  // FNV-1a based digest, for illustration only (urgap uses md5/blake2).
  const fnv = (str, seed) => {
    let h = 0x811c9dc5 ^ seed;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 0x01000193);
    }
    return (h >>> 0).toString(16).padStart(8, "0");
  };
  const digest = (str) => {
    const full = fnv(str, 0) + fnv(str, 0x9e3779b9) + fnv(str, 0x7f4a7c15) + fnv(str, 0x2545f491);
    return `${full.slice(0, 4)}…${full.slice(-4)}`;
  };

  const q = document.getElementById("pac-q");
  const t = document.getElementById("pac-t");
  const tOut = document.getElementById("pac-t-out");
  const v = document.getElementById("pac-v");
  const segTool = document.getElementById("seg-tool");
  const segParams = document.getElementById("seg-params");
  const status = document.getElementById("pac-status");

  if (q && t && v) {
    // Mirrors urgap: sorted parameter JSON, minus parameters_not_triggering_rerun.
    const rerunKey = () => JSON.stringify({ "-q": q.value.trim() });
    const initial = { key: rerunKey(), version: v.value };
    let last = { ...initial };

    const flash = (el) => {
      el.classList.remove("flash");
      void el.offsetWidth;
      el.classList.add("flash");
      setTimeout(() => el.classList.remove("flash"), 700);
    };

    const render = (source) => {
      const key = rerunKey();
      const version = v.value;
      segTool.textContent = `FilterTabularToCSV_${version.replaceAll(".", "_")}`;
      segParams.textContent = digest(key);
      tOut.textContent = t.value;

      if (key !== last.key) flash(segParams);
      if (version !== last.version) flash(segTool);
      last = { key, version };

      const unchanged = key === initial.key && version === initial.version;
      status.classList.toggle("is-new", !unchanged);
      if (unchanged) {
        status.innerHTML =
          source === "threads"
            ? "Threads changed, name unchanged → still <strong>skipped</strong>."
            : "Same inputs, same parameters → same name → <strong>skipped</strong>.";
      } else {
        status.innerHTML = "New name → this step <strong>runs once</strong>, and is reused from then on.";
      }
    };

    q.addEventListener("input", () => render("query"));
    v.addEventListener("change", () => render("version"));
    t.addEventListener("input", () => render("threads"));
    render("init");
  }

  // ---- smart rerun DAG ----
  const scenarios = {
    first: { skip: [], caption: "Every step runs once and writes outputs named by its provenance." },
    align: {
      skip: ["fastqc", "trim", "ref", "index"],
      caption: "Alignment parameters changed: QC, trimming and indexing are reused. Only alignment and what follows it run.",
    },
    again: {
      skip: ["fastqc", "trim", "ref", "index", "align", "sort"],
      caption: "Nothing changed: every expected output already exists, so nothing is recomputed.",
    },
  };
  const chips = document.querySelectorAll(".dag .chip");
  const nodes = document.querySelectorAll(".dag__svg .node");
  const caption = document.getElementById("dag-caption");
  const setScenario = (name) => {
    const s = scenarios[name];
    nodes.forEach((n) => n.classList.toggle("is-skip", s.skip.includes(n.dataset.step)));
    chips.forEach((c) => {
      const on = c.dataset.scenario === name;
      c.classList.toggle("is-active", on);
      c.setAttribute("aria-selected", String(on));
    });
    caption.textContent = s.caption;
  };
  chips.forEach((c) => c.addEventListener("click", () => setScenario(c.dataset.scenario)));

  // ---- agent chat playback ----
  const chat = document.getElementById("chat");
  const replay = document.getElementById("agent-replay");
  let timers = [];
  const play = () => {
    timers.forEach(clearTimeout);
    timers = [];
    const msgs = [...chat.querySelectorAll(".msg")];
    if (reduceMotion) {
      msgs.forEach((m) => m.classList.add("is-in"));
      return;
    }
    msgs.forEach((m) => m.classList.remove("is-in"));
    let delay = 200;
    msgs.forEach((m) => {
      timers.push(setTimeout(() => m.classList.add("is-in"), delay));
      delay += m.classList.contains("msg--tool") ? 550 : 1000;
    });
  };
  if (chat) {
    const chatObserver = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          play();
          chatObserver.disconnect();
        }
      },
      { threshold: 0.35 }
    );
    chatObserver.observe(chat);
    replay?.addEventListener("click", play);
  }

  // ---- copy buttons ----
  document.querySelectorAll(".copy[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const src = document.getElementById(btn.dataset.copy);
      try {
        await navigator.clipboard.writeText(src.innerText.trim());
        btn.textContent = "Copied";
        btn.classList.add("is-done");
      } catch {
        btn.textContent = "Select & copy";
      }
      setTimeout(() => {
        btn.textContent = "Copy";
        btn.classList.remove("is-done");
      }, 1600);
    });
  });
})();

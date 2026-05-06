(function () {
  const key = "sql-query-optimizer-theme";

  function readTheme() {
    try {
      return localStorage.getItem(key) || "dark";
    } catch (error) {
      return "dark";
    }
  }

  function writeTheme(theme) {
    try {
      localStorage.setItem(key, theme);
    } catch (error) {
      return;
    }
  }

  function applyTheme(theme) {
    const isDark = theme === "dark";
    document.body.classList.toggle("dark", isDark);

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      const label = window.sqlI18n
        ? window.sqlI18n.t(isDark ? "theme.light" : "theme.dark")
        : isDark
          ? "Ganti ke mode normal"
          : "Ganti ke mode dark";
      button.setAttribute("aria-label", label);
      button.title = label;
    });
  }

  function initTheme() {
    applyTheme(readTheme());

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.addEventListener("click", () => {
        const nextTheme = document.body.classList.contains("dark") ? "light" : "dark";
        writeTheme(nextTheme);
        applyTheme(nextTheme);
      });
    });

    document.addEventListener("sql-language-change", () => applyTheme(readTheme()));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTheme);
  } else {
    initTheme();
  }
})();

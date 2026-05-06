(function () {
  const key = "sql-query-optimizer-language";

  const translations = {
    id: {
      "action.clear": "Bersihkan",
      "action.copy": "Salin",
      "action.format": "Format SQL",
      "action.optimize": "Optimisasi Query",
      "action.sample": "Contoh Query",
      "common.dialectAria": "Pilih dialek SQL",
      "common.inputSql": "Input SQL",
      "formatter.emptyFormatted": "Belum ada hasil. Masukkan SQL lalu klik Format SQL.",
      "formatter.eyebrow": "Python SQL formatter",
      "formatter.inputCopy": "Tempel query mentah yang ingin dirapikan.",
      "formatter.placeholder": "select o.id,o.created_at,c.email from orders o join customers c on o.customer_id=c.id where o.status='paid' order by o.created_at desc limit 100;",
      "formatter.resultCopy": "Output hanya merapikan struktur query tanpa mengubah logika.",
      "formatter.resultTitle": "SQL formatted",
      "formatter.title": "Format SQL",
      "landing.copy": "Pilih workflow yang dibutuhkan: optimisasi query dengan penjelasan performa atau format SQL agar query lebih mudah dibaca.",
      "landing.eyebrow": "Python SQL assistant",
      "landing.featureAria": "Pilih fitur",
      "landing.formatCopy": "Rapikan query mentah menjadi struktur SQL yang konsisten, mudah discan, dan nyaman dipakai untuk review.",
      "landing.formatTitle": "Format SQL",
      "landing.metadataCopy": "Aplikasi tidak mengetahui index, partition, ukuran tabel, statistik data, atau execution plan. Semua saran perlu divalidasi dengan database target.",
      "landing.metadataTitle": "Metadata-blind",
      "landing.notesAria": "Catatan aplikasi",
      "landing.openFormatter": "Buka Formatter",
      "landing.openOptimizer": "Buka Optimizer",
      "landing.optimizeCopy": "Analisis pola query, tampilkan rewrite yang disarankan, dan jelaskan risiko performa tanpa mengasumsikan index atau partition key.",
      "landing.optimizeTitle": "Optimize SQL",
      "landing.pythonCopy": "Logika utama ada di <code>app.py</code> dan berjalan di browser memakai Pyodide, sehingga tetap bisa dideploy ke GitHub Pages.",
      "landing.pythonTitle": "Berjalan dengan Python",
      "nav.format": "Format SQL",
      "nav.home": "Home",
      "nav.optimize": "Optimize SQL",
      "optimizer.confidence": "Keyakinan",
      "optimizer.editorAria": "Editor SQL optimizer",
      "optimizer.emptyOptimized": "Belum ada hasil. Masukkan SQL lalu jalankan optimisasi.",
      "optimizer.emptyReviewCopy": "Analyzer akan menandai pola seperti <code>SELECT *</code>, fungsi di kolom filter, <code>NOT IN</code>, dan pagination offset.",
      "optimizer.emptyReviewTitle": "Belum ada review.",
      "optimizer.eyebrow": "Python metadata-blind SQL optimizer",
      "optimizer.explanationCopy": "Alasan dan prioritas perbaikan berdasarkan pola query, bukan metadata fisik tabel.",
      "optimizer.explanationTitle": "Penjelasan optimisasi",
      "optimizer.inputCopy": "Tempel query yang ingin dianalisis dan dioptimisasi.",
      "optimizer.note": "Analisis ini tidak memakai metadata tabel. Saran index atau partition hanya berupa kandidat yang perlu divalidasi dengan <code>EXPLAIN</code>, statistik, dan workload nyata.",
      "optimizer.placeholder": "SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id WHERE DATE(o.created_at) = '2026-05-01' ORDER BY o.created_at DESC LIMIT 100;",
      "optimizer.playbookAria": "Prinsip optimisasi SQL",
      "optimizer.playbookTitle": "Yang bisa dianalisis tanpa metadata",
      "optimizer.resultCopy": "Rewrite aman hanya diterapkan jika polanya cukup jelas.",
      "optimizer.resultTitle": "Query hasil optimisasi yang disarankan",
      "optimizer.rewriteChance": "Peluang rewrite",
      "optimizer.scanRisk": "Risiko scan",
      "optimizer.scoreAria": "Skor kualitas query",
      "optimizer.scoreTitle": "Skor kualitas query",
      "optimizer.summaryAria": "Ringkasan analisis",
      "optimizer.summaryTitle": "Ringkasan AI",
      "optimizer.title": "Optimize SQL",
      "playbook.ioCopy": "Pilih kolom yang dibutuhkan, batasi sorting global, dan hindari dedup mahal seperti <code>DISTINCT</code> atau <code>UNION</code> jika tidak perlu.",
      "playbook.ioTitle": "I/O hemat",
      "playbook.joinCopy": "Filter baris lebih awal, pastikan join punya kondisi, dan agregasi detail sebelum join ketika hasil akhirnya memang agregat.",
      "playbook.joinTitle": "Join lebih kecil",
      "playbook.sargable": "Hindari fungsi atau cast di sisi kolom filter. Gunakan range eksplisit agar optimizer punya peluang memakai akses terarah.",
      "playbook.validateCopy": "Gunakan <code>EXPLAIN ANALYZE</code>, runtime, rows scanned, spill, dan shuffle metrics sebelum menganggap query sudah optimal.",
      "playbook.validateTitle": "Validasi eksekusi",
      "state.fallbackActive": "Fallback aktif",
      "state.fallbackFormatter": "Fallback formatter aktif",
      "state.fallbackOptimizer": "Fallback optimizer aktif",
      "state.fallbackReady": "Fallback siap",
      "state.formatted": "Formatted",
      "state.loadingPython": "Memuat Python",
      "state.noInput": "Menunggu input",
      "state.pythonReady": "Python siap",
      "state.reviewNeeded": "Perlu review",
      "state.goodEnough": "Cukup baik",
      "theme.dark": "Ganti ke mode dark",
      "theme.light": "Ganti ke mode normal",
    },
    en: {
      "action.clear": "Clear",
      "action.copy": "Copy",
      "action.format": "Format SQL",
      "action.optimize": "Optimize Query",
      "action.sample": "Sample Query",
      "common.dialectAria": "Choose SQL dialect",
      "common.inputSql": "SQL Input",
      "formatter.emptyFormatted": "No result yet. Enter SQL, then click Format SQL.",
      "formatter.eyebrow": "Python SQL formatter",
      "formatter.inputCopy": "Paste the raw query you want to format.",
      "formatter.placeholder": "select o.id,o.created_at,c.email from orders o join customers c on o.customer_id=c.id where o.status='paid' order by o.created_at desc limit 100;",
      "formatter.resultCopy": "The output only restructures the query without changing its logic.",
      "formatter.resultTitle": "Formatted SQL",
      "formatter.title": "Format SQL",
      "landing.copy": "Choose the workflow you need: optimize a query with performance explanations or format SQL so it is easier to read.",
      "landing.eyebrow": "Python SQL assistant",
      "landing.featureAria": "Choose a feature",
      "landing.formatCopy": "Turn raw SQL into a consistent, readable structure that is easier to scan and review.",
      "landing.formatTitle": "Format SQL",
      "landing.metadataCopy": "The app does not know indexes, partitions, table size, data statistics, or execution plans. Validate every suggestion against the target database.",
      "landing.metadataTitle": "Metadata-blind",
      "landing.notesAria": "Application notes",
      "landing.openFormatter": "Open Formatter",
      "landing.openOptimizer": "Open Optimizer",
      "landing.optimizeCopy": "Analyze query patterns, show suggested rewrites, and explain performance risk without assuming indexes or partition keys.",
      "landing.optimizeTitle": "Optimize SQL",
      "landing.pythonCopy": "The main logic lives in <code>app.py</code> and runs in the browser through Pyodide, so the app can still be deployed to GitHub Pages.",
      "landing.pythonTitle": "Runs With Python",
      "nav.format": "Format SQL",
      "nav.home": "Home",
      "nav.optimize": "Optimize SQL",
      "optimizer.confidence": "Confidence",
      "optimizer.editorAria": "SQL optimizer editor",
      "optimizer.emptyOptimized": "No result yet. Enter SQL, then run optimization.",
      "optimizer.emptyReviewCopy": "The analyzer will flag patterns such as <code>SELECT *</code>, functions on filtered columns, <code>NOT IN</code>, and offset pagination.",
      "optimizer.emptyReviewTitle": "No review yet.",
      "optimizer.eyebrow": "Python metadata-blind SQL optimizer",
      "optimizer.explanationCopy": "Reasons and priorities based on query patterns, not physical table metadata.",
      "optimizer.explanationTitle": "Optimization Explanation",
      "optimizer.inputCopy": "Paste the query you want to analyze and optimize.",
      "optimizer.note": "This analysis does not use table metadata. Index or partition suggestions are only candidates that must be validated with <code>EXPLAIN</code>, statistics, and real workload.",
      "optimizer.placeholder": "SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id WHERE DATE(o.created_at) = '2026-05-01' ORDER BY o.created_at DESC LIMIT 100;",
      "optimizer.playbookAria": "SQL optimization principles",
      "optimizer.playbookTitle": "What can be analyzed without metadata",
      "optimizer.resultCopy": "Safe rewrites are applied only when the pattern is clear enough.",
      "optimizer.resultTitle": "Suggested Optimized Query",
      "optimizer.rewriteChance": "Rewrite options",
      "optimizer.scanRisk": "Scan risk",
      "optimizer.scoreAria": "Query quality score",
      "optimizer.scoreTitle": "Query quality score",
      "optimizer.summaryAria": "Analysis summary",
      "optimizer.summaryTitle": "AI Summary",
      "optimizer.title": "Optimize SQL",
      "playbook.ioCopy": "Select only needed columns, limit global sorting, and avoid expensive deduplication such as <code>DISTINCT</code> or <code>UNION</code> when unnecessary.",
      "playbook.ioTitle": "Lean I/O",
      "playbook.joinCopy": "Filter rows early, ensure joins have predicates, and pre-aggregate detail data before joins when the final result is aggregated.",
      "playbook.joinTitle": "Smaller joins",
      "playbook.sargable": "Avoid functions or casts on filtered columns. Use explicit ranges so the optimizer has a better chance to use targeted access.",
      "playbook.validateCopy": "Use <code>EXPLAIN ANALYZE</code>, runtime, rows scanned, spills, and shuffle metrics before assuming the query is optimized.",
      "playbook.validateTitle": "Validate execution",
      "state.fallbackActive": "Fallback active",
      "state.fallbackFormatter": "Fallback formatter active",
      "state.fallbackOptimizer": "Fallback optimizer active",
      "state.fallbackReady": "Fallback ready",
      "state.formatted": "Formatted",
      "state.loadingPython": "Loading Python",
      "state.noInput": "Waiting for input",
      "state.pythonReady": "Python ready",
      "state.reviewNeeded": "Needs review",
      "state.goodEnough": "Looks good",
      "theme.dark": "Switch to dark mode",
      "theme.light": "Switch to normal mode",
    },
  };

  function readLanguage() {
    try {
      return localStorage.getItem(key) || "id";
    } catch (error) {
      return "id";
    }
  }

  function writeLanguage(language) {
    try {
      localStorage.setItem(key, language);
    } catch (error) {
      return;
    }
  }

  function t(name, language = window.sqlLanguage || readLanguage()) {
    return translations[language]?.[name] || translations.id[name] || name;
  }

  function applyLanguage(language) {
    window.sqlLanguage = language;
    document.documentElement.lang = language;

    document.querySelectorAll("[data-i18n]").forEach((element) => {
      if (element.id === "analysisState") {
        const current = element.textContent.trim();
        const statusKey = Object.keys(translations.id).find((name) => {
          if (!name.startsWith("state.")) return false;
          return translations.id[name] === current || translations.en[name] === current;
        });
        element.textContent = t(statusKey || element.dataset.i18n, language);
        return;
      }

      const value = t(element.dataset.i18n, language);
      if (value.includes("<")) {
        element.innerHTML = value;
      } else {
        element.textContent = value;
      }
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
      element.setAttribute("placeholder", t(element.dataset.i18nPlaceholder, language));
    });

    document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
      element.setAttribute("aria-label", t(element.dataset.i18nAria, language));
    });

    document.querySelectorAll("[data-language]").forEach((button) => {
      button.classList.toggle("is-active", button.dataset.language === language);
      button.setAttribute("aria-pressed", String(button.dataset.language === language));
    });

    document.dispatchEvent(new CustomEvent("sql-language-change", { detail: { language } }));
  }

  function rerunPythonTool() {
    if (!window.pythonSqlAppReady || !window.pyodide) return;

    const input = document.getElementById("sqlInput");
    if (!input || !input.value.trim()) return;

    if (document.getElementById("optimizeButton")) {
      window.pyodide.runPython("run_optimization()");
    } else if (document.getElementById("formatButton")) {
      window.pyodide.runPython("run_formatting_only()");
    }
  }

  function init() {
    const language = readLanguage();
    applyLanguage(language);

    document.querySelectorAll("[data-language]").forEach((button) => {
      button.addEventListener("click", () => {
        const nextLanguage = button.dataset.language;
        writeLanguage(nextLanguage);
        applyLanguage(nextLanguage);
        rerunPythonTool();
      });
    });
  }

  window.sqlI18n = { applyLanguage, t };
  window.sqlLanguage = readLanguage();

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

(function () {
  const sampleSql = `select * from orders o
join customers c on o.customer_id = c.id
where date(o.created_at) = '2026-05-01'
  and lower(c.email) like '%@example.com'
  or o.status in ('paid','settled')
order by o.created_at desc
limit 100 offset 5000;`;

  const clauses = [
    "SELECT",
    "FROM",
    "WHERE",
    "GROUP BY",
    "ORDER BY",
    "HAVING",
    "LIMIT",
    "OFFSET",
    "UNION ALL",
    "UNION",
    "INNER JOIN",
    "LEFT OUTER JOIN",
    "RIGHT OUTER JOIN",
    "FULL OUTER JOIN",
    "LEFT JOIN",
    "RIGHT JOIN",
    "FULL JOIN",
    "CROSS JOIN",
    "JOIN",
    "ON",
  ];

  const keywords = [
    "select",
    "from",
    "where",
    "join",
    "inner",
    "left",
    "right",
    "full",
    "cross",
    "outer",
    "on",
    "and",
    "or",
    "group",
    "by",
    "order",
    "having",
    "limit",
    "offset",
    "union",
    "all",
    "distinct",
    "not",
    "in",
    "exists",
    "like",
    "between",
    "is",
    "null",
    "asc",
    "desc",
  ];

  function get(id) {
    return document.getElementById(id);
  }

  function setText(id, value) {
    const element = get(id);
    if (element) element.textContent = value;
  }

  function t(key, fallback) {
    return window.sqlI18n ? window.sqlI18n.t(key) : fallback;
  }

  function normalize(sql) {
    return sql.replace(/\s+/g, " ").trim();
  }

  function titleForState(value) {
    setText("analysisState", value.includes(".") ? t(value, value) : value);
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => {
      const entities = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      };
      return entities[char];
    });
  }

  function uppercaseKeywords(sql) {
    let output = sql;
    keywords.forEach((keyword) => {
      output = output.replace(new RegExp(`\\b${keyword}\\b`, "gi"), keyword.toUpperCase());
    });
    return output;
  }

  function addOneDay(value) {
    const date = new Date(`${value}T00:00:00Z`);
    date.setUTCDate(date.getUTCDate() + 1);
    return date.toISOString().slice(0, 10);
  }

  function formatSql(sql) {
    let text = normalize(sql);
    if (!text) return "";

    text = uppercaseKeywords(text);
    text = text.replace(/\s*,\s*/g, ", ");

    clauses.forEach((clause) => {
      text = text.replace(new RegExp(`\\s+${clause.replace(" ", "\\s+")}\\b`, "gi"), `\n${clause}`);
    });

    text = text.replace(/\s+(AND|OR)\s+/g, "\n  $1 ");

    const lines = text
      .split(/\n+/)
      .map((line) => line.trim())
      .filter(Boolean);

    const formatted = [];
    lines.forEach((line) => {
      const upper = line.toUpperCase();
      if (upper.startsWith("SELECT ")) {
        const selectBody = line.slice(7).trim();
        formatted.push("SELECT");
        selectBody.split(/\s*,\s*/).forEach((part, index, items) => {
          const suffix = index < items.length - 1 ? "," : "";
          formatted.push(`  ${part}${suffix}`);
        });
        return;
      }

      if (upper === "SELECT" || upper === "WHERE" || upper === "HAVING") {
        formatted.push(upper);
        return;
      }

      if (upper.startsWith("WHERE ")) {
        formatted.push("WHERE");
        formatted.push(`  ${line.slice(6).trim()}`);
        return;
      }

      if (/^(AND|OR)\b/i.test(line)) {
        formatted.push(`  ${line}`);
        return;
      }

      formatted.push(line);
    });

    return formatted.join("\n");
  }

  function analyzeFallback(sql) {
    const normalized = normalize(sql);
    const findings = [];
    const rewrites = [];
    let optimized = normalized;

    if (/select\s+\*/i.test(normalized)) {
      findings.push([
        "HIGH",
        window.sqlLanguage === "en" ? "SELECT * increases I/O" : "SELECT * meningkatkan I/O",
        window.sqlLanguage === "en" ? "Replace it with the columns that are actually needed." : "Ganti dengan daftar kolom yang benar-benar dibutuhkan.",
      ]);
      optimized = optimized.replace(
        /select\s+\*/i,
        window.sqlLanguage === "en"
          ? "SELECT /* choose only used columns: col_1, col_2, ... */ *"
          : "SELECT /* pilih kolom yang dipakai: col_1, col_2, ... */ *",
      );
      rewrites.push(window.sqlLanguage === "en" ? "SELECT * was marked because table schema is unavailable." : "SELECT * diberi penanda karena skema tabel tidak tersedia.");
    }

    const dateMatch = optimized.match(/\bdate\s*\(\s*([a-z_][\w.]*)\s*\)\s*=\s*'(\d{4}-\d{2}-\d{2})'/i);
    if (dateMatch) {
      const nextDate = addOneDay(dateMatch[2]);
      optimized = optimized.replace(dateMatch[0], `${dateMatch[1]} >= '${dateMatch[2]}' AND ${dateMatch[1]} < '${nextDate}'`);
      findings.push([
        "HIGH",
        window.sqlLanguage === "en" ? "Function on filtered column is not SARGable" : "Fungsi di kolom filter tidak SARGable",
        window.sqlLanguage === "en" ? "Rewrite DATE(column) into an explicit range." : "Ubah DATE(column) menjadi range eksplisit.",
      ]);
      rewrites.push(window.sqlLanguage === "en" ? "DATE(column) = 'YYYY-MM-DD' was rewritten into a half-open range." : "DATE(column) = 'YYYY-MM-DD' diubah menjadi half-open range.");
    }

    if (/like\s+['"]%/i.test(normalized)) {
      findings.push([
        "HIGH",
        window.sqlLanguage === "en" ? "LIKE with a leading wildcard is hard to optimize" : "LIKE dengan wildcard di depan sulit memakai akses terarah",
        window.sqlLanguage === "en" ? "Use prefix search, full-text search, or tokenization." : "Gunakan prefix search, full-text search, atau strategi tokenisasi.",
      ]);
    }

    if (/\boffset\s+\d{4,}/i.test(normalized)) {
      findings.push([
        "MEDIUM",
        window.sqlLanguage === "en" ? "Large OFFSET makes pagination slower" : "OFFSET besar membuat pagination makin lambat",
        window.sqlLanguage === "en" ? "Consider keyset pagination." : "Pertimbangkan keyset pagination.",
      ]);
    }

    return { optimized: formatSql(optimized), findings, rewrites };
  }

  function renderFallbackReview(result) {
    const review = get("reviewList");
    const reviewText = get("reviewText");
    if (!review) return;

    if (!result.findings.length) {
      review.innerHTML = `
        <article class="empty-state">
          <strong>${window.sqlLanguage === "en" ? "No major risk pattern detected." : "Tidak ada pola risiko besar yang terdeteksi."}</strong>
          <span>${window.sqlLanguage === "en" ? "Still validate with EXPLAIN because fallback does not know table metadata." : "Tetap validasi dengan EXPLAIN karena fallback tidak mengetahui metadata tabel."}</span>
        </article>
      `;
      if (reviewText) reviewText.value = window.sqlLanguage === "en" ? "No major risk pattern detected. Validation with EXPLAIN is still required." : "Tidak ada pola risiko besar yang terdeteksi. Validasi tetap perlu dilakukan dengan EXPLAIN.";
      return;
    }

    const rewriteHtml = result.rewrites.length
      ? `<article class="finding"><div class="finding-head"><h3>${window.sqlLanguage === "en" ? "Automatic rewrite" : "Rewrite otomatis"}</h3><span class="severity low">Info</span></div><p>${escapeHtml(result.rewrites.join(" "))}</p></article>`
      : "";

    review.innerHTML =
      rewriteHtml +
      result.findings
        .map(
          ([severity, title, suggestion]) => `
            <article class="finding">
              <div class="finding-head">
                <h3>${escapeHtml(title)}</h3>
                <span class="severity ${severity.toLowerCase()}">${severity}</span>
              </div>
              <p><strong>${window.sqlLanguage === "en" ? "Suggestion" : "Saran"}:</strong> ${escapeHtml(suggestion)}</p>
            </article>
          `,
        )
        .join("");

    if (reviewText) {
      reviewText.value = result.findings.map(([severity, title, suggestion]) => `[${severity}] ${title}\n${window.sqlLanguage === "en" ? "Suggestion" : "Saran"}: ${suggestion}`).join("\n\n");
    }
  }

  function runFormatFallback() {
    if (window.pythonSqlAppReady) return;
    const input = get("sqlInput");
    const sql = input ? input.value.trim() : "";
    if (!sql) {
      setText("formattedSql", t("formatter.emptyFormatted", "Belum ada hasil. Masukkan SQL terlebih dahulu."));
      titleForState("state.noInput");
      return;
    }
    setText("formattedSql", formatSql(sql));
    titleForState("state.fallbackFormatter");
  }

  function runOptimizeFallback() {
    if (window.pythonSqlAppReady) return;
    const input = get("sqlInput");
    const sql = input ? input.value.trim() : "";
    if (!sql) {
      setText("optimizedSql", t("optimizer.emptyOptimized", "Belum ada hasil. Masukkan SQL lalu jalankan optimisasi."));
      renderFallbackReview({ findings: [], rewrites: [] });
      titleForState("state.noInput");
      return;
    }

    const result = analyzeFallback(sql);
    setText("optimizedSql", result.optimized);
    renderFallbackReview(result);
    setText("scanRisk", result.findings.length ? (window.sqlLanguage === "en" ? "Medium" : "Sedang") : (window.sqlLanguage === "en" ? "Low" : "Rendah"));
    setText("rewriteCount", String(result.rewrites.length));
    setText("confidence", "Fallback");
    const score = get("scoreValue");
    if (score) score.textContent = String(Math.max(35, 96 - result.findings.length * 14));
    titleForState("state.fallbackOptimizer");
  }

  function clearFallback() {
    if (window.pythonSqlAppReady) return;
    const input = get("sqlInput");
    if (input) input.value = "";
    if (get("formatButton")) runFormatFallback();
    if (get("optimizeButton")) runOptimizeFallback();
    if (input) input.focus();
  }

  function loadSampleFallback() {
    if (window.pythonSqlAppReady) return;
    const input = get("sqlInput");
    if (input) input.value = sampleSql;
    if (get("formatButton")) runFormatFallback();
    if (get("optimizeButton")) runOptimizeFallback();
  }

  function copyFallback(targetId, button) {
    if (window.pythonSqlAppReady) return;
    const target = get(targetId);
    if (!target) return;
    const text = target.value || target.textContent;
    navigator.clipboard?.writeText(text);
    const original = button.textContent;
    button.textContent = window.sqlLanguage === "en" ? "Copied" : "Tersalin";
    setTimeout(() => {
      button.textContent = original;
    }, 1200);
  }

  function enableActions() {
    ["loadSample", "optimizeButton", "formatButton", "clearButton"].forEach((id) => {
      const element = get(id);
      if (element) element.disabled = false;
    });
  }

  function bind() {
    enableActions();
    get("formatButton")?.addEventListener("click", runFormatFallback);
    get("optimizeButton")?.addEventListener("click", runOptimizeFallback);
    get("clearButton")?.addEventListener("click", clearFallback);
    get("loadSample")?.addEventListener("click", loadSampleFallback);

    document.querySelectorAll("[data-copy]").forEach((button) => {
      button.addEventListener("click", () => copyFallback(button.dataset.copy, button));
    });

    get("sqlInput")?.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        if (get("formatButton")) runFormatFallback();
        if (get("optimizeButton")) runOptimizeFallback();
      }
    });

    if (get("formatButton") || get("optimizeButton")) {
      titleForState("state.fallbackReady");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();

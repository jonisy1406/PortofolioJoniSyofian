import html

from scripts.formatter import format_sql
from scripts.optimizer import analyze_sql

try:
    from js import document, setTimeout, window
    from pyodide.ffi import create_proxy
except ImportError:
    document = None
    setTimeout = None
    window = None
    create_proxy = None


SAMPLE_SQL = """select * from orders o
join customers c on o.customer_id = c.id
where date(o.created_at) = '2026-05-01'
  and lower(c.email) like '%@example.com'
  or o.status in ('paid','settled')
order by o.created_at desc
limit 100 offset 5000;"""

PROXIES = []

TEXT = {
    "id": {
        "auto_rewrite": "Rewrite otomatis",
        "copied": "Tersalin",
        "empty_formatted": "Belum ada hasil. Masukkan SQL terlebih dahulu.",
        "empty_optimized": "Belum ada hasil. Masukkan SQL lalu jalankan optimisasi.",
        "empty_review_copy": "Analyzer akan menandai pola seperti <code>SELECT *</code>, fungsi di kolom filter, <code>NOT IN</code>, dan pagination offset.",
        "empty_review_title": "Belum ada review.",
        "fallback_not_used": "Optimisasi belum dijalankan. Klik Optimisasi Query untuk analisis performa.",
        "formatted": "Formatted",
        "good_enough": "Cukup baik",
        "keyakinan": "Keyakinan",
        "no_major": "Tidak ada pola risiko besar yang terdeteksi.",
        "pattern": "Pola",
        "python_ready": "Python siap",
        "review_header": "SQL Query Optimization Review",
        "risk": "Risiko scan",
        "suggestion": "Saran",
        "validate": "Tetap validasi dengan EXPLAIN karena analyzer tidak mengetahui index, partition, ukuran tabel, atau distribusi data.",
        "validate_text": "Tidak ada pola risiko besar yang terdeteksi. Validasi tetap perlu dilakukan dengan EXPLAIN.",
        "waiting": "Menunggu input",
        "review_needed": "Perlu review",
    },
    "en": {
        "auto_rewrite": "Automatic rewrite",
        "copied": "Copied",
        "empty_formatted": "No result yet. Enter SQL first.",
        "empty_optimized": "No result yet. Enter SQL, then run optimization.",
        "empty_review_copy": "The analyzer will flag patterns such as <code>SELECT *</code>, functions on filtered columns, <code>NOT IN</code>, and offset pagination.",
        "empty_review_title": "No review yet.",
        "fallback_not_used": "Optimization has not been run yet. Click Optimize Query for performance analysis.",
        "formatted": "Formatted",
        "good_enough": "Looks good",
        "keyakinan": "Confidence",
        "no_major": "No major risk pattern detected.",
        "pattern": "Pattern",
        "python_ready": "Python ready",
        "review_header": "SQL Query Optimization Review",
        "risk": "Scan risk",
        "suggestion": "Suggestion",
        "validate": "Still validate with EXPLAIN because the analyzer does not know indexes, partitions, table size, or data distribution.",
        "validate_text": "No major risk pattern detected. Validation with EXPLAIN is still required.",
        "waiting": "Waiting for input",
        "review_needed": "Needs review",
    },
}


def get_language():
    if window is None:
        return "id"
    language = getattr(window, "sqlLanguage", "id")
    return "en" if language == "en" else "id"


def tr(key):
    return TEXT[get_language()][key]


def escape_html(value):
    return html.escape(str(value), quote=True)


def get_element(element_id):
    return document.getElementById(element_id)


def has_element(element_id):
    return get_element(element_id) is not None


def set_text(element_id, value):
    element = get_element(element_id)
    if element is not None:
        element.textContent = value


def set_value(element_id, value):
    element = get_element(element_id)
    if element is not None:
        element.value = value


def set_actions_enabled(enabled):
    for element_id in ("loadSample", "optimizeButton", "formatButton", "clearButton"):
        element = get_element(element_id)
        if element is not None:
            element.disabled = not enabled


def update_score(score):
    if not has_element("scoreValue") or not has_element("scoreRing"):
        return

    circumference = 364.4
    offset = circumference - (score / 100) * circumference
    get_element("scoreValue").textContent = str(score)
    get_element("scoreRing").style.strokeDashoffset = str(offset)


def render_findings(result):
    review_list = get_element("reviewList")
    review_text = get_element("reviewText")
    findings = result["findings"]

    if not findings:
        review_list.innerHTML = """
          <article class="empty-state">
            <strong>{title}</strong>
            <span>{copy}</span>
          </article>
        """.format(title=tr("no_major"), copy=tr("validate"))
        review_text.value = tr("validate_text")
        return

    rewrite_section = ""
    if result["rewrites"]:
        rewrite_section = f"""
          <article class="finding">
            <div class="finding-head">
              <h3>{tr("auto_rewrite")}</h3>
              <span class="severity low">Info</span>
            </div>
            <p>{escape_html(' '.join(result["rewrites"]))}</p>
          </article>
        """

    finding_cards = []
    for finding in findings:
        finding_cards.append(
            f"""
            <article class="finding">
              <div class="finding-head">
                <h3>{escape_html(finding["title"])}</h3>
                <span class="severity {finding["severity"]}">{finding["severity"].upper()}</span>
              </div>
              <p><strong>{tr("pattern")}:</strong> <code>{escape_html(finding["pattern"])}</code></p>
              <p>{escape_html(finding["detail"])}</p>
              <p><strong>{tr("suggestion")}:</strong> {escape_html(finding["recommendation"])}</p>
            </article>
            """
        )

    review_list.innerHTML = rewrite_section + "".join(finding_cards)

    review_lines = [
        tr("review_header"),
        f"Score: {result['score']}/100",
        f"{tr('risk')}: {result['scanRisk']}",
        f"{tr('keyakinan')}: {result['confidence']}",
        "",
    ]
    review_lines.extend([f"Rewrite: {rewrite}" for rewrite in result["rewrites"]])
    review_lines.append("")

    for index, finding in enumerate(findings, start=1):
        review_lines.append(
            "\n".join(
                [
                    f"{index}. [{finding['severity'].upper()}] {finding['title']}",
                    f"{tr('pattern')}: {finding['pattern']}",
                    f"Detail: {finding['detail']}",
                    f"{tr('suggestion')}: {finding['recommendation']}",
                ]
            )
        )

    review_text.value = "\n".join(review_lines)


def run_optimization(event=None):
    sql = get_element("sqlInput").value
    result = analyze_sql(sql, get_element("dialect").value, get_language())

    if not sql.strip():
        set_text("optimizedSql", tr("empty_optimized"))
        set_text("formattedSql", tr("fallback_not_used"))
        get_element("reviewList").innerHTML = f"""
          <article class="empty-state">
            <strong>{tr("empty_review_title")}</strong>
            <span>{tr("empty_review_copy")}</span>
          </article>
        """
        set_value("reviewText", "")
        update_score(0)
        set_text("scanRisk", "-")
        set_text("rewriteCount", "0")
        set_text("confidence", "-")
        set_text("analysisState", tr("waiting"))
        return

    set_text("optimizedSql", result["optimized"])
    set_text("formattedSql", result["formatted"])
    render_findings(result)
    update_score(result["score"])
    set_text("scanRisk", result["scanRisk"])
    set_text("rewriteCount", str(len(result["rewrites"])))
    set_text("confidence", result["confidence"])
    set_text("analysisState", tr("review_needed") if result["findings"] else tr("good_enough"))


def run_formatting_only(event=None):
    sql = get_element("sqlInput").value.strip()
    if not sql:
        set_text("formattedSql", tr("empty_formatted"))
        set_text("analysisState", tr("waiting"))
        return

    set_text("formattedSql", format_sql(sql))
    set_text("optimizedSql", tr("fallback_not_used"))
    set_text("analysisState", tr("formatted"))


def clear_all(event=None):
    get_element("sqlInput").value = ""
    if has_element("optimizeButton"):
        run_optimization()
    else:
        run_formatting_only()
    get_element("sqlInput").focus()


def load_sample(event=None):
    get_element("sqlInput").value = SAMPLE_SQL
    if has_element("optimizeButton"):
        run_optimization()
    elif has_element("formatButton"):
        run_formatting_only()


def copy_text_from(target_id, button):
    element = get_element(target_id)
    if element is None:
        return

    text = element.value or element.textContent
    if not text.strip():
        return

    helper = document.createElement("textarea")
    helper.value = text
    helper.setAttribute("readonly", "")
    helper.className = "sr-only"
    document.body.appendChild(helper)
    helper.select()
    document.execCommand("copy")
    helper.remove()

    original = button.textContent
    button.textContent = tr("copied")

    def reset_text(*args):
        button.textContent = original

    proxy = create_proxy(reset_text)
    PROXIES.append(proxy)
    setTimeout(proxy, 1200)


def bind_click(element, handler):
    proxy = create_proxy(lambda event: handler(event))
    PROXIES.append(proxy)
    element.addEventListener("click", proxy)


def boot():
    if has_element("loadSample"):
        bind_click(get_element("loadSample"), load_sample)

    if has_element("optimizeButton"):
        bind_click(get_element("optimizeButton"), run_optimization)

    if has_element("formatButton"):
        bind_click(get_element("formatButton"), run_formatting_only)

    if has_element("clearButton"):
        bind_click(get_element("clearButton"), clear_all)

    for button in document.querySelectorAll("[data-copy]"):
        bind_click(button, lambda event, button=button: copy_text_from(button.dataset.copy, button))

    def on_keydown(event):
        if (event.ctrlKey or event.metaKey) and event.key == "Enter":
            if has_element("optimizeButton"):
                run_optimization()
            elif has_element("formatButton"):
                run_formatting_only()

    keydown_proxy = create_proxy(on_keydown)
    PROXIES.append(keydown_proxy)
    if has_element("sqlInput"):
        get_element("sqlInput").addEventListener("keydown", keydown_proxy)

    update_score(0)
    set_actions_enabled(True)
    set_text("analysisState", tr("python_ready"))

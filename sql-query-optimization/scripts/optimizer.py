import datetime
import re

from scripts.formatter import format_sql

FINDING_TRANSLATIONS = {
    "SELECT * meningkatkan I/O": (
        "SELECT * increases I/O",
        "The query reads every column, so the database may scan and transfer data that is not used.",
        "Replace it with the columns that are actually needed. The analyzer cannot infer column names without schema metadata.",
    ),
    "Fungsi di kolom filter membuat predicate tidak SARGable": (
        "Function on filtered column makes the predicate non-SARGable",
        "Patterns such as DATE(column) or LOWER(column) often force row-by-row evaluation before filtering.",
        "Rewrite it as a range or store a normalized derived value. Date example: column >= '2026-05-01' AND column < '2026-05-02'.",
    ),
    "LIKE dengan wildcard di depan sulit memakai akses terarah": (
        "LIKE with a leading wildcard is hard to optimize",
        "LIKE '%text' usually requires a scan because the value prefix is unknown.",
        "Use prefix search when possible, full-text/search indexes, or tokenized columns depending on the product need.",
    ),
    "NOT IN sensitif terhadap NULL": (
        "NOT IN is sensitive to NULL",
        "If the subquery returns NULL, NOT IN can produce unexpected results and may be harder to optimize.",
        "Use NOT EXISTS with an explicit join predicate, then ensure the comparison column is non-null if required.",
    ),
    "IN subquery berpotensi lebih mahal pada data besar": (
        "IN subquery can be expensive on large data",
        "Modern optimizers often rewrite this pattern, but the result depends on the database and statistics.",
        "Consider EXISTS or an explicit semi-join when the relationship and selectivity are clear.",
    ),
    "UNION melakukan deduplikasi": (
        "UNION performs deduplication",
        "UNION needs sorting or hashing to remove duplicates, which is more expensive than UNION ALL.",
        "Use UNION ALL if duplicates are acceptable or impossible.",
    ),
    "DISTINCT dan GROUP BY bisa redundan": (
        "DISTINCT and GROUP BY may be redundant",
        "Both can force deduplication or aggregation work.",
        "Check whether DISTINCT is still needed after GROUP BY.",
    ),
    "DISTINCT bisa menutup akar duplikasi": (
        "DISTINCT can hide the root cause of duplication",
        "DISTINCT is often used to mask duplicates caused by broad joins.",
        "Validate join cardinality. If duplicates are not needed, fix the join or pre-aggregate the source.",
    ),
    "OFFSET besar membuat pagination makin lambat": (
        "Large OFFSET makes pagination slower",
        "The database still has to skip many rows before returning the requested page.",
        "Use keyset pagination with an anchor condition such as created_at < :last_seen_created_at.",
    ),
    "ORDER BY tanpa pembatas bisa mahal": (
        "ORDER BY without a limit can be expensive",
        "A global sort over a large result can use significant memory or spill to disk.",
        "Add LIMIT/FETCH if only a subset is needed, or sort after the most selective filters.",
    ),
    "Filter non-agregat di HAVING terlambat dieksekusi": (
        "Non-aggregate filter in HAVING is applied late",
        "HAVING runs after GROUP BY, so rows that could have been removed earlier are still processed.",
        "Move non-aggregate filters to WHERE if the logic is equivalent.",
    ),
    "OR dapat mengurangi selektivitas filter": (
        "OR can reduce filter selectivity",
        "Several OR branches on different columns can make the optimizer choose a scan.",
        "If each branch is highly selective, test a UNION ALL rewrite and handle duplicates explicitly.",
    ),
    "Ada JOIN tanpa kondisi ON yang jelas": (
        "JOIN without a clear ON condition detected",
        "A join without a predicate can multiply rows and greatly increase cost.",
        "Make sure every JOIN has an appropriate ON or USING condition.",
    ),
    "Fungsi pada kolom join membuat join lebih mahal": (
        "Function on join column makes the join more expensive",
        "Join predicates with casts or per-row transformations can prevent efficient join strategies.",
        "Align data types and value formats at the source, then join directly on prepared columns.",
    ),
    "Scalar subquery di SELECT dapat dieksekusi berulang": (
        "Scalar subquery in SELECT may run repeatedly",
        "On some databases, a per-row subquery can significantly increase cost.",
        "Consider pre-aggregation followed by JOIN, or use a window function when appropriate.",
    ),
    "BETWEEN tanggal bisa melewatkan data waktu": (
        "Date BETWEEN can miss timestamp data",
        "BETWEEN is inclusive and can be wrong when the column stores timestamps.",
        "Use a half-open range: >= start_date AND < next_end_date.",
    ),
}

REWRITE_TRANSLATIONS = {
    "DATE(column) = 'YYYY-MM-DD' diubah menjadi half-open range.": "DATE(column) = 'YYYY-MM-DD' was rewritten into a half-open range.",
    "UNION diberi alternatif UNION ALL untuk menghindari deduplikasi mahal.": "UNION was changed to a UNION ALL alternative to avoid expensive deduplication.",
    "NOT IN subquery sederhana diubah menjadi NOT EXISTS.": "A simple NOT IN subquery was rewritten as NOT EXISTS.",
    "IN subquery sederhana diubah menjadi EXISTS.": "A simple IN subquery was rewritten as EXISTS.",
    "SELECT * diberi penanda karena kolom tidak dapat ditebak tanpa skema.": "SELECT * was marked because column names cannot be inferred without schema metadata.",
    "Untuk BigQuery, pastikan filter partition column ditambahkan jika tabel dipartisi. Analyzer tidak tahu nama partition key.": "For BigQuery, ensure a partition-column filter is added when the table is partitioned. The analyzer does not know the partition key.",
    "Tidak ada rewrite otomatis yang cukup aman; rekomendasi tersedia di checklist review.": "No automatic rewrite was safe enough; recommendations are available in the review checklist.",
}

METRIC_TRANSLATIONS = {
    "Tinggi": "High",
    "Sedang": "Medium",
    "Rendah-Sedang": "Low-Medium",
    "Rendah": "Low",
    "Sedang-Tinggi": "Medium-High",
}


def normalize_whitespace(sql):
    return re.sub(r"\s+", " ", sql).strip()


def create_finding(severity, title, detail, recommendation, pattern):
    return {
        "severity": severity,
        "title": title,
        "detail": detail,
        "recommendation": recommendation,
        "pattern": pattern,
    }


def has_pattern(sql, pattern):
    return re.search(pattern, sql, re.IGNORECASE) is not None


def extract_select_list(sql):
    match = re.search(r"\bselect\b([\s\S]+?)\bfrom\b", sql, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def estimate_scan_risk(findings):
    high = len([finding for finding in findings if finding["severity"] == "high"])
    medium = len([finding for finding in findings if finding["severity"] == "medium"])

    if high >= 2 or (high == 1 and medium >= 3):
        return "Tinggi"
    if high == 1 or medium >= 2:
        return "Sedang"
    if medium == 1:
        return "Rendah-Sedang"
    return "Rendah"


def estimate_confidence(sql, findings):
    if not sql.strip():
        return "-"
    if any(finding["severity"] == "high" for finding in findings):
        return "Sedang"
    if findings:
        return "Sedang-Tinggi"
    return "Tinggi"


def score_query(findings):
    penalty = 0
    for finding in findings:
        if finding["severity"] == "high":
            penalty += 18
        elif finding["severity"] == "medium":
            penalty += 10
        else:
            penalty += 5
    return max(35, min(96, 96 - penalty))


def localize_finding(finding, language):
    if language != "en":
        return finding

    translated = FINDING_TRANSLATIONS.get(finding["title"])
    if not translated:
        return finding

    title, detail, recommendation = translated
    return {
        **finding,
        "title": title,
        "detail": detail,
        "recommendation": recommendation,
    }


def localize_rewrite(rewrite, language):
    if language != "en":
        return rewrite
    return REWRITE_TRANSLATIONS.get(rewrite, rewrite)


def localize_metric(value, language):
    if language != "en":
        return value
    return METRIC_TRANSLATIONS.get(value, value)


def analyze_sql(sql, dialect, language="id"):
    normalized = normalize_whitespace(sql)
    lower = normalized.lower()
    findings = []
    rewrites = []

    if not normalized:
        return {
            "formatted": "",
            "optimized": "",
            "findings": [],
            "score": 0,
            "scanRisk": "-",
            "confidence": "-",
            "rewrites": [],
        }

    select_list = extract_select_list(normalized)

    if re.search(r"^\s*(distinct\s+)?\*", select_list, re.IGNORECASE) or re.search(r",\s*\*", select_list):
        findings.append(
            create_finding(
                "high",
                "SELECT * meningkatkan I/O",
                "Query mengambil semua kolom sehingga database harus membaca dan mengirim data yang mungkin tidak dipakai.",
                "Ganti dengan daftar kolom yang benar-benar dibutuhkan. Analyzer tidak bisa menebak nama kolom tanpa skema.",
                "SELECT *",
            )
        )

    if has_pattern(
        normalized,
        r"\b(date|year|month|day|lower|upper|trim|substring|substr|cast|convert)\s*\([^)]*\b[a-z_][\w.]*[^)]*\)\s*(=|<|>|between|like)",
    ):
        findings.append(
            create_finding(
                "high",
                "Fungsi di kolom filter membuat predicate tidak SARGable",
                "Pola seperti DATE(column) atau LOWER(column) sering memaksa evaluasi per baris sebelum filter.",
                "Ubah menjadi range atau simpan nilai turunan yang sudah dinormalisasi. Contoh tanggal: column >= '2026-05-01' AND column < '2026-05-02'.",
                "function(column)",
            )
        )

    if has_pattern(normalized, r"\blike\s+['\"]%[^'\"]+['\"]"):
        findings.append(
            create_finding(
                "high",
                "LIKE dengan wildcard di depan sulit memakai akses terarah",
                "LIKE '%teks' biasanya membutuhkan scan karena awalan nilai tidak diketahui.",
                "Gunakan pencarian prefix jika memungkinkan, full-text/search index, atau kolom tokenisasi sesuai kebutuhan produk.",
                "LIKE '%...'",
            )
        )

    if has_pattern(normalized, r"\bnot\s+in\s*\("):
        findings.append(
            create_finding(
                "medium",
                "NOT IN sensitif terhadap NULL",
                "Jika subquery mengandung NULL, hasil NOT IN bisa tidak sesuai ekspektasi dan rencana eksekusi dapat lebih sulit dioptimalkan.",
                "Gunakan NOT EXISTS dengan kondisi join eksplisit, lalu pastikan kolom pembanding tidak NULL jika memang diperlukan.",
                "NOT IN",
            )
        )

    if has_pattern(normalized, r"\bin\s*\(\s*select\b"):
        findings.append(
            create_finding(
                "medium",
                "IN subquery berpotensi lebih mahal pada data besar",
                "Optimizer modern sering bisa menulis ulang pola ini, tetapi hasilnya bergantung pada database dan statistik.",
                "Pertimbangkan EXISTS atau semi-join eksplisit ketika relasi dan selektivitasnya jelas.",
                "IN (SELECT ...)",
            )
        )

    if has_pattern(normalized, r"\bunion\b(?!\s+all)"):
        findings.append(
            create_finding(
                "medium",
                "UNION melakukan deduplikasi",
                "UNION perlu sort/hash untuk menghapus duplikat sehingga lebih mahal daripada UNION ALL.",
                "Gunakan UNION ALL jika duplikat memang boleh muncul atau sudah tidak mungkin terjadi.",
                "UNION",
            )
        )

    if has_pattern(normalized, r"\bdistinct\b") and has_pattern(normalized, r"\bgroup\s+by\b"):
        findings.append(
            create_finding(
                "medium",
                "DISTINCT dan GROUP BY bisa redundan",
                "Keduanya sama-sama dapat memaksa deduplikasi atau agregasi.",
                "Periksa apakah DISTINCT masih diperlukan setelah GROUP BY.",
                "DISTINCT + GROUP BY",
            )
        )
    elif has_pattern(normalized, r"\bdistinct\b"):
        findings.append(
            create_finding(
                "low",
                "DISTINCT bisa menutup akar duplikasi",
                "DISTINCT sering dipakai untuk menyembunyikan duplikasi dari join yang terlalu lebar.",
                "Validasi cardinality join. Jika duplikasi tidak dibutuhkan, perbaiki join atau pre-aggregate sumbernya.",
                "DISTINCT",
            )
        )

    if has_pattern(normalized, r"\boffset\s+\d{4,}"):
        findings.append(
            create_finding(
                "medium",
                "OFFSET besar membuat pagination makin lambat",
                "Database tetap perlu melewati banyak baris sebelum mengembalikan halaman yang diminta.",
                "Gunakan keyset pagination dengan kondisi anchor seperti created_at < :last_seen_created_at.",
                "OFFSET besar",
            )
        )

    if has_pattern(normalized, r"\border\s+by\b") and not has_pattern(normalized, r"\blimit\b|\bfetch\b"):
        findings.append(
            create_finding(
                "low",
                "ORDER BY tanpa pembatas bisa mahal",
                "Sorting global pada hasil besar dapat memakai memori besar atau spill ke disk.",
                "Tambahkan LIMIT/FETCH jika hanya butuh sebagian baris, atau sort di tahap akhir setelah filter paling selektif.",
                "ORDER BY",
            )
        )

    if has_pattern(normalized, r"\bhaving\b"):
        having_text = re.split(r"\bhaving\b", lower, flags=re.IGNORECASE, maxsplit=1)[1]
        if not re.search(r"\b(count|sum|avg|min|max)\s*\(", having_text, re.IGNORECASE):
            findings.append(
                create_finding(
                    "medium",
                    "Filter non-agregat di HAVING terlambat dieksekusi",
                    "HAVING berjalan setelah GROUP BY sehingga baris yang seharusnya bisa dibuang lebih awal tetap ikut diproses.",
                    "Pindahkan filter non-agregat ke WHERE jika logikanya sama.",
                    "HAVING",
                )
            )

    if has_pattern(normalized, r"\b(or)\b"):
        findings.append(
            create_finding(
                "medium",
                "OR dapat mengurangi selektivitas filter",
                "Beberapa OR pada kolom berbeda bisa membuat optimizer memilih scan.",
                "Jika setiap cabang sangat selektif, uji rewrite menjadi UNION ALL dan tangani duplikasi secara eksplisit.",
                "OR",
            )
        )

    if has_pattern(normalized, r"\bjoin\b"):
        join_count = len(re.findall(r"\bjoin\b", normalized, re.IGNORECASE))
        on_count = len(re.findall(r"\bon\b", normalized, re.IGNORECASE))

        if on_count < join_count and not has_pattern(normalized, r"\bcross\s+join\b"):
            findings.append(
                create_finding(
                    "high",
                    "Ada JOIN tanpa kondisi ON yang jelas",
                    "Join tanpa predicate bisa menghasilkan perkalian baris dan ledakan biaya.",
                    "Pastikan setiap JOIN punya kondisi ON atau USING yang sesuai relasi data.",
                    "JOIN tanpa ON",
                )
            )

        if has_pattern(normalized, r"\bon\s+[^=]*(cast|convert|lower|upper|trim)\s*\("):
            findings.append(
                create_finding(
                    "high",
                    "Fungsi pada kolom join membuat join lebih mahal",
                    "Join predicate yang memakai cast atau transformasi per baris dapat menghambat strategi join yang efisien.",
                    "Samakan tipe data dan format nilai di sumber data, lalu join langsung pada kolom yang sudah siap.",
                    "function(join_column)",
                )
            )

    if has_pattern(normalized, r"\bselect\b[\s\S]+\(\s*select\b"):
        findings.append(
            create_finding(
                "medium",
                "Scalar subquery di SELECT dapat dieksekusi berulang",
                "Pada beberapa database, subquery per baris meningkatkan biaya secara signifikan.",
                "Pertimbangkan pre-aggregation lalu JOIN, atau gunakan window function bila sesuai.",
                "SELECT (SELECT ...)",
            )
        )

    if has_pattern(normalized, r"\bbetween\s+['\"]\d{4}-\d{2}-\d{2}['\"]\s+and\s+['\"]\d{4}-\d{2}-\d{2}['\"]"):
        findings.append(
            create_finding(
                "low",
                "BETWEEN tanggal bisa melewatkan data waktu",
                "BETWEEN bersifat inklusif dan berisiko salah jika kolom menyimpan timestamp.",
                "Gunakan half-open range: >= tanggal_awal AND < tanggal_akhir_plus_1.",
                "BETWEEN tanggal",
            )
        )

    optimized = build_optimized_sql(normalized, dialect, findings, rewrites, language)
    formatted = format_sql(normalized)
    localized_findings = [localize_finding(finding, language) for finding in findings]
    localized_rewrites = [localize_rewrite(rewrite, language) for rewrite in rewrites]

    return {
        "formatted": formatted,
        "optimized": optimized or formatted,
        "findings": localized_findings,
        "score": score_query(findings),
        "scanRisk": localize_metric(estimate_scan_risk(findings), language),
        "confidence": localize_metric(estimate_confidence(normalized, findings), language),
        "rewrites": localized_rewrites,
    }


def build_optimized_sql(sql, dialect, findings, rewrites, language="id"):
    next_sql = sql

    date_pattern = re.compile(
        r"\bdate\s*\(\s*([a-z_][\w.]*)\s*\)\s*=\s*'(\d{4}-\d{2}-\d{2})'",
        re.IGNORECASE,
    )
    date_match = date_pattern.search(next_sql)
    if date_match:
        column = date_match.group(1)
        date_value = date_match.group(2)
        next_date = add_one_day(date_value)
        next_sql = date_pattern.sub(
            f"{column} >= '{date_value}' AND {column} < '{next_date}'",
            next_sql,
            count=1,
        )
        rewrites.append("DATE(column) = 'YYYY-MM-DD' diubah menjadi half-open range.")

    union_pattern = re.compile(r"\bunion\b(?!\s+all)", re.IGNORECASE)
    if union_pattern.search(next_sql):
        next_sql = union_pattern.sub(
            "UNION ALL /* pakai UNION jika duplikasi harus dihapus */",
            next_sql,
            count=1,
        )
        rewrites.append("UNION diberi alternatif UNION ALL untuk menghindari deduplikasi mahal.")

    not_in_pattern = re.compile(
        r"([a-z_][\w.]*)\s+not\s+in\s*\(\s*select\s+([a-z_][\w.]*)\s+from\s+([a-z_][\w.]*)(?:\s+where\s+([^)]+))?\)",
        re.IGNORECASE,
    )
    not_in_match = not_in_pattern.search(next_sql)
    if not_in_match:
        outer_column = not_in_match.group(1)
        inner_column = not_in_match.group(2)
        inner_table = not_in_match.group(3)
        inner_filter = not_in_match.group(4)
        filter_sql = f" AND {inner_filter}" if inner_filter else ""
        replacement = (
            f"NOT EXISTS (SELECT 1 FROM {inner_table} anti "
            f"WHERE anti.{inner_column.split('.')[-1]} = {outer_column}{filter_sql})"
        )
        next_sql = not_in_pattern.sub(replacement, next_sql, count=1)
        rewrites.append("NOT IN subquery sederhana diubah menjadi NOT EXISTS.")

    in_pattern = re.compile(
        r"([a-z_][\w.]*)\s+in\s*\(\s*select\s+([a-z_][\w.]*)\s+from\s+([a-z_][\w.]*)(?:\s+where\s+([^)]+))?\)",
        re.IGNORECASE,
    )
    in_match = in_pattern.search(next_sql)
    if in_match and not re.search(r"not\s+exists", next_sql, re.IGNORECASE):
        outer_column = in_match.group(1)
        inner_column = in_match.group(2)
        inner_table = in_match.group(3)
        inner_filter = in_match.group(4)
        filter_sql = f" AND {inner_filter}" if inner_filter else ""
        replacement = (
            f"EXISTS (SELECT 1 FROM {inner_table} semi "
            f"WHERE semi.{inner_column.split('.')[-1]} = {outer_column}{filter_sql})"
        )
        next_sql = in_pattern.sub(replacement, next_sql, count=1)
        rewrites.append("IN subquery sederhana diubah menjadi EXISTS.")

    select_list = extract_select_list(next_sql)
    if re.match(r"^\s*\*", select_list):
        next_sql = re.sub(
            r"\bselect\s+\*",
            "SELECT /* choose only used columns: col_1, col_2, ... */ *"
            if language == "en"
            else "SELECT /* pilih kolom yang dipakai: col_1, col_2, ... */ *",
            next_sql,
            count=1,
            flags=re.IGNORECASE,
        )
        rewrites.append("SELECT * diberi penanda karena kolom tidak dapat ditebak tanpa skema.")

    if dialect == "bigquery" and has_pattern(next_sql, r"\blimit\b") and not has_pattern(next_sql, r"\bwhere\b"):
        rewrites.append(
            "Untuk BigQuery, pastikan filter partition column ditambahkan jika tabel dipartisi. Analyzer tidak tahu nama partition key."
        )

    if findings and not rewrites:
        rewrites.append("Tidak ada rewrite otomatis yang cukup aman; rekomendasi tersedia di checklist review.")

    return format_sql(next_sql)


def add_one_day(date_value):
    year, month, day = [int(part) for part in date_value.split("-")]
    date = datetime.date(year, month, day) + datetime.timedelta(days=1)
    return date.isoformat()

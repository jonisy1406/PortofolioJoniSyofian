import re


KEYWORDS = {
    "SELECT",
    "FROM",
    "WHERE",
    "JOIN",
    "LEFT",
    "RIGHT",
    "INNER",
    "OUTER",
    "FULL",
    "CROSS",
    "ON",
    "AND",
    "OR",
    "GROUP",
    "BY",
    "ORDER",
    "HAVING",
    "LIMIT",
    "OFFSET",
    "FETCH",
    "UNION",
    "ALL",
    "DISTINCT",
    "CASE",
    "WHEN",
    "THEN",
    "ELSE",
    "END",
    "AS",
    "IN",
    "EXISTS",
    "NOT",
    "NULL",
    "IS",
    "BETWEEN",
    "LIKE",
    "WITH",
    "OVER",
    "PARTITION",
    "INSERT",
    "UPDATE",
    "DELETE",
    "CREATE",
    "ALTER",
    "DROP",
    "ASC",
    "DESC",
}

BREAK_BEFORE = {
    "SELECT",
    "FROM",
    "WHERE",
    "GROUP BY",
    "ORDER BY",
    "HAVING",
    "LIMIT",
    "OFFSET",
    "FETCH",
    "UNION",
    "UNION ALL",
}

JOIN_PREFIXES = {
    "JOIN",
    "INNER JOIN",
    "LEFT JOIN",
    "LEFT OUTER JOIN",
    "RIGHT JOIN",
    "RIGHT OUTER JOIN",
    "FULL JOIN",
    "FULL OUTER JOIN",
    "CROSS JOIN",
}

TOKEN_PATTERN = re.compile(
    r"('[^']*(?:''[^']*)*'|\"[^\"]*\"|`[^`]*`|\[[^\]]+\]|--.*?$|/\*[\s\S]*?\*/|>=|<=|<>|!=|::|\|\||\b\w+\b|[(),;=<>!*+\-/]|\S)",
    re.IGNORECASE | re.MULTILINE,
)


def tokenize(sql):
    tokens = []

    for match in TOKEN_PATTERN.finditer(sql):
        value = match.group(0)

        if value.startswith("--") or value.startswith("/*"):
            tokens.append({"value": value, "type": "comment"})
        elif re.match(r"^['\"`\[]", value):
            tokens.append({"value": value, "type": "literal"})
        elif re.match(r"^\w+$", value):
            upper = value.upper()
            tokens.append(
                {
                    "value": upper if upper in KEYWORDS else value,
                    "type": "keyword" if upper in KEYWORDS else "word",
                }
            )
        else:
            tokens.append({"value": value, "type": "symbol"})

    return tokens


def join_multi_word_keyword(tokens, index):
    current = tokens[index]["value"].upper() if index < len(tokens) else ""
    next_value = tokens[index + 1]["value"].upper() if index + 1 < len(tokens) else ""
    third = tokens[index + 2]["value"].upper() if index + 2 < len(tokens) else ""

    if current == "GROUP" and next_value == "BY":
        return {"keyword": "GROUP BY", "skip": 1}
    if current == "ORDER" and next_value == "BY":
        return {"keyword": "ORDER BY", "skip": 1}
    if current == "UNION" and next_value == "ALL":
        return {"keyword": "UNION ALL", "skip": 1}
    if current == "INNER" and next_value == "JOIN":
        return {"keyword": "INNER JOIN", "skip": 1}
    if current == "LEFT" and next_value == "JOIN":
        return {"keyword": "LEFT JOIN", "skip": 1}
    if current == "RIGHT" and next_value == "JOIN":
        return {"keyword": "RIGHT JOIN", "skip": 1}
    if current == "FULL" and next_value == "JOIN":
        return {"keyword": "FULL JOIN", "skip": 1}
    if current == "CROSS" and next_value == "JOIN":
        return {"keyword": "CROSS JOIN", "skip": 1}
    if current == "LEFT" and next_value == "OUTER" and third == "JOIN":
        return {"keyword": "LEFT OUTER JOIN", "skip": 2}
    if current == "RIGHT" and next_value == "OUTER" and third == "JOIN":
        return {"keyword": "RIGHT OUTER JOIN", "skip": 2}
    if current == "FULL" and next_value == "OUTER" and third == "JOIN":
        return {"keyword": "FULL OUTER JOIN", "skip": 2}

    return None


def needs_space_before(token, previous):
    if not previous:
        return False
    if token in {",", ";", ")"}:
        return False
    if previous == "(":
        return False
    if token in {".", "::"} or previous in {".", "::"}:
        return False
    return True


def clean_line(line):
    line = re.sub(r"\s+([,;)])", r"\1", line)
    line = re.sub(r"\(\s+", "(", line)
    line = re.sub(r"\s+\.", ".", line)
    line = re.sub(r"\.\s+", ".", line)
    line = re.sub(r"\s{2,}", " ", line)
    return line.strip()


def format_sql(sql):
    trimmed = sql.strip()
    if not trimmed:
        return ""

    tokens = tokenize(trimmed)
    lines = []
    line = ""
    indent = 0
    clause_indent = 0
    current_clause = ""
    previous = ""
    index = 0

    def push_line():
        nonlocal line, previous
        cleaned = clean_line(line)
        if cleaned:
            lines.append(f"{'  ' * max(indent + clause_indent, 0)}{cleaned}")
        line = ""
        previous = ""

    while index < len(tokens):
        token = tokens[index]
        multi = join_multi_word_keyword(tokens, index)
        value = multi["keyword"] if multi else token["value"]
        if multi:
            index += multi["skip"]

        upper = value.upper()

        if token["type"] == "comment":
            push_line()
            lines.append(f"{'  ' * max(indent + clause_indent, 0)}{value}")
            index += 1
            continue

        if upper == ")":
            indent = max(0, indent - 1)
            if line.strip() == "":
                line = f"{'  ' * indent})"
            else:
                line += ")"
            previous = ")"
            index += 1
            continue

        if upper in BREAK_BEFORE or upper in JOIN_PREFIXES:
            push_line()
            clause_indent = 0
            line = value
            previous = value
            current_clause = upper
            if upper in {"SELECT", "WHERE", "HAVING"}:
                push_line()
                clause_indent = 1
            index += 1
            continue

        if upper in {"AND", "OR", "WHEN", "ELSE"}:
            push_line()
            line = value
            previous = value
            if current_clause in {"WHERE", "HAVING", "ON"}:
                clause_indent = 1
            index += 1
            continue

        if upper == "ON":
            push_line()
            clause_indent = 0
            line = "ON"
            previous = value
            current_clause = "ON"
            index += 1
            continue

        if value == ",":
            line += ","
            push_line()
            previous = ","
            index += 1
            continue

        if value == "(":
            if needs_space_before(value, previous) and not re.search(
                r"\b(COUNT|SUM|AVG|MIN|MAX|DATE|LOWER|UPPER|CAST|COALESCE)$",
                previous,
                re.IGNORECASE,
            ):
                line += " "
            line += "("
            indent += 1
            previous = "("
            index += 1
            continue

        if value == ";":
            line += ";"
            push_line()
            index += 1
            continue

        if needs_space_before(value, previous):
            line += " "
        line += value
        previous = value
        index += 1

    push_line()
    return "\n".join(lines)

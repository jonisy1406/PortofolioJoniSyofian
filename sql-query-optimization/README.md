# SQL Query Optimization Assistant

SQL Query Optimization Assistant is a static web application for formatting, reviewing, and optimizing SQL queries directly in the browser.

The optimizer is rule-based. It uses Python heuristics to detect common SQL performance risks and suggest safe rewrites where the pattern is clear enough.

The project is designed for cases where the user only provides raw SQL text. The application does not require table schemas, indexes, partition keys, table size, data statistics, or execution plans.

## Features

- Rule-based SQL optimizer powered by Python in the browser.
- SQL formatter for turning raw SQL into a cleaner, more readable structure.
- Metadata-blind SQL analysis for common performance risks.
- Suggested query rewrites when the pattern is safe enough to rewrite.
- Optimization explanation shown directly below the suggested optimized query.
- Query quality score from 0 to 100.
- Scan risk, rewrite count, and confidence summary.
- Separate pages for `Optimize SQL` and `Format SQL`.
- Bahasa Indonesia and English UI.
- Optimizer review output supports Bahasa Indonesia and English.
- Dark and normal mode toggle.
- Copy buttons for generated output.
- Sample SQL button.
- Fallback JavaScript logic when Pyodide cannot be loaded.
- Responsive design styled to match the visual direction of `portofoliojonisyofian.com`.

## Tech Stack

- HTML for page structure.
- CSS for responsive styling and dark-first visual design.
- Python for SQL formatting, query analysis, optimization heuristics, scoring, and DOM binding.
- Pyodide to run Python in the browser.
- JavaScript for language switching, theme switching, Pyodide loading, and fallback behavior.
- GitHub Pages for static deployment.

## Project Structure

```text
.
|-- app.py
|-- index.html
|-- README.md
|-- assets
|   |-- css
|   |   `-- styles.css
|   `-- js
|       |-- fallback.js
|       |-- i18n.js
|       |-- pyodide-loader.js
|       `-- theme.js
|-- pages
|   |-- format.html
|   `-- optimize.html
`-- scripts
    |-- __init__.py
    |-- dom_app.py
    |-- formatter.py
    `-- optimizer.py
```

## File Responsibilities

- `index.html`: Landing page for choosing between optimizer and formatter.
- `pages/optimize.html`: SQL optimization page.
- `pages/format.html`: SQL formatter page.
- `assets/css/styles.css`: Main website styling.
- `assets/js/i18n.js`: Bahasa Indonesia and English translation handling.
- `assets/js/theme.js`: Dark and normal mode handling.
- `assets/js/fallback.js`: Lightweight fallback logic if Pyodide fails to load.
- `assets/js/pyodide-loader.js`: Loads Pyodide and registers Python modules into Pyodide's virtual filesystem.
- `app.py`: Python entrypoint executed by Pyodide.
- `scripts/formatter.py`: SQL formatter logic.
- `scripts/optimizer.py`: SQL analyzer, optimizer heuristics, rewrite logic, scoring, and bilingual review output.
- `scripts/dom_app.py`: Python DOM binding and event handling for Pyodide.

## How It Works

GitHub Pages only serves static files, so this project does not use a Python backend.

The browser workflow is:

1. The user opens the landing page.
2. The user chooses either `Optimize SQL` or `Format SQL`.
3. The page loads Pyodide from CDN.
4. `assets/js/pyodide-loader.js` writes the Python modules from `scripts/` into Pyodide's virtual filesystem.
5. Pyodide runs `app.py`.
6. Python binds the page buttons and processes the SQL input in the browser.

If Pyodide cannot be loaded, `assets/js/fallback.js` keeps the core buttons usable with lightweight JavaScript formatting and optimization hints.

## Analysis Limitations

The optimizer is intentionally metadata-blind. It does not know:

- Available indexes.
- Primary keys or foreign keys.
- Partition keys.
- Table size.
- Data distribution.
- Database statistics.
- Actual execution plans.

Because of this, all recommendations should be treated as an initial review. Validate any rewrite using the target database, real workload, and execution metrics.

Recommended validation tools:

- `EXPLAIN`
- `EXPLAIN ANALYZE`
- Query runtime comparison
- Rows scanned
- Actual index usage
- Scan bytes, spill, or shuffle metrics for analytical engines

## Detected Query Patterns

The optimizer checks for patterns such as:

- `SELECT *`
- Function calls on filtered columns, for example `DATE(column)` or `LOWER(column)`
- Leading-wildcard search such as `LIKE '%value'`
- `NOT IN`
- `IN (SELECT ...)`
- `UNION` versus `UNION ALL`
- `DISTINCT`
- Large `OFFSET`
- Non-aggregate filters in `HAVING`
- Broad `OR` predicates
- Joins without clear `ON` predicates
- Functions on join columns
- Scalar subqueries in `SELECT`
- Date `BETWEEN` on timestamp-like columns

## Running Locally

Do not open `index.html` directly through `file://`, because the browser may block `fetch()` calls for Python modules and assets.

From the portfolio repository root, run a local static server:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/sql-query-optimization/
```

Tool pages:

```text
http://localhost:8000/sql-query-optimization/pages/optimize.html
http://localhost:8000/sql-query-optimization/pages/format.html
```

If the static server is started from inside the `sql-query-optimization` folder instead, open `http://localhost:8000/`.

## Deploying to GitHub Pages

1. Push all project files and folders to a GitHub repository.
2. Open the repository `Settings`.
3. Go to `Pages`.
4. Under `Build and deployment`, select `Deploy from a branch`.
5. Select the main branch, for example `main`.
6. Select the repository root folder.
7. Save the configuration.
8. Wait for GitHub Pages to publish the site.

## Deployment Notes

The application loads Pyodide from a CDN, so internet access is required when the optimizer or formatter page first loads Python.

If the CDN is blocked or unavailable, the fallback JavaScript logic still provides basic formatter and optimizer behavior.

For fully offline hosting, Pyodide assets must be self-hosted inside the project or on another static asset server.

## Validation Performed

The project has been validated with:

```bash
python -m py_compile app.py scripts\formatter.py scripts\optimizer.py scripts\dom_app.py
node --check assets\js\i18n.js
node --check assets\js\theme.js
node --check assets\js\fallback.js
node --check assets\js\pyodide-loader.js
```

Static routes were also checked locally:

- `/`
- `/pages/optimize.html`
- `/pages/format.html`
- `/assets/js/i18n.js`
- `/assets/css/styles.css`
- `/scripts/dom_app.py`

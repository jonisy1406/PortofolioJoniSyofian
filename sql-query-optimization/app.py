from scripts.dom_app import boot, document, run_formatting_only, run_optimization
from scripts.formatter import format_sql
from scripts.optimizer import analyze_sql


if document is not None:
    boot()

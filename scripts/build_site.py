#!/usr/bin/env python3
"""Build the static ACE-U report site from the checked-in sample export."""

from pathlib import Path
import subprocess
import sys

import markdown


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SAMPLE = ROOT / "examples" / "sample-export.json"


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    reports = {
        "markdown": ROOT / "generated-report.md",
        "json": SITE / "report.json",
        "sarif": SITE / "report.sarif",
    }
    for output_format, output_path in reports.items():
        subprocess.run(
            [
                sys.executable,
                "-m",
                "aceu_entra_trust.cli",
                "--input",
                str(SAMPLE),
                "--format",
                output_format,
                "--out",
                str(output_path),
            ],
            cwd=ROOT,
            check=True,
        )

    report_markdown = reports["markdown"].read_text(encoding="utf-8")
    reports["markdown"].unlink()
    report_html = markdown.markdown(report_markdown, extensions=["tables"])
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ACE-U Entra Trust Report</title>
  <style>
    body {{ max-width: 920px; margin: 3rem auto; padding: 0 1.25rem; font: 16px/1.6 system-ui, sans-serif; color: #172033; }}
    a {{ color: #0759a5; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #d5dbe5; padding: .55rem; text-align: left; }}
    th {{ background: #f3f6fa; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <header>
    <nav aria-label="Related resources">
      <a href="report.json">JSON report</a> ·
      <a href="report.sarif">SARIF report</a> ·
      <a href="https://github.com/sanandani/entra-trust-demo">Repository</a> ·
      <a href="https://imshubh.com">Project homepage</a>
    </nav>
  </header>
  <main>{report_html}</main>
</body>
</html>
"""
    (SITE / "index.html").write_text(page, encoding="utf-8")
if __name__ == "__main__":
    main()

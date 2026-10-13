# Truelove–Witts ulcerative colitis severity calculator

An adult ulcerative colitis severity assessment based on the modified Truelove and Witts criteria. The repository includes a zero-dependency Python CLI and a static, client-side browser calculator in [web/](web/).

**Clinical use:** Educational decision support only. This is not a diagnosis or treatment protocol. Suspected acute severe ulcerative colitis (ASUC) is a medical emergency warranting urgent hospital assessment.

## How the classification works

**Severe** requires **at least six stools/day with visible blood**, and **at least one** systemic toxicity marker:

- Pulse >90 beats/minute
- Temperature >37.8°C
- Haemoglobin <10.5 g/dL
- ESR >30 mm/hour
- CRP >30 mg/L (modified criterion)

**Mild** is fewer than four stools/day with none/small amounts of blood and normal-range values on the assessed mild-severity variables (pulse <90, temperature <37.5°C, haemoglobin >11.5 g/dL, ESR <20 when measured, CRP ≤5 mg/L when measured). The CRP mild-range cutoff of 5 mg/L is a pragmatic assumption; reference ranges vary across laboratories. **Moderate** comprises cases not meeting mild or severe patterns.

For **six or more visibly bloody stools/day**, the absence of a positive systemic marker cannot rule out ASUC when ESR or CRP is missing. Such cases are labeled **Indeterminate**, not negative. A positive marker establishes severe classification even if other markers are unavailable.

Threshold comparisons follow the cited criteria strictly (e.g. 90 bpm is not >90 bpm). This is a categorical rule set, **not a numerical severity score**. Results are not validated to predict outcomes.

Sources: [NICE NG130: UC management, Truelove and Witts severity index](https://www.nice.org.uk/guidance/ng130/chapter/Recommendations) and [BSG inflammatory bowel disease guidelines, 2025](https://doi.org/10.1136/gutjnl-2024-334395).

## Browser calculator

The complete static app is in [web/index.html](web/index.html). It runs using native JavaScript, with no dependencies or server-side Python. Start a local static server to test:

~~~bash
python -m http.server 8000 --directory web
~~~

Open http://localhost:8000. The form has no patient identifiers, analytics, cookies, remote script calls, or persistence; submitted observations remain in browser memory only. Deployment to GitHub Pages is configured by [the Pages workflow](.github/workflows/pages.yml), subject to Pages being enabled for the repository.

## Python CLI

Python 3.10+ is supported, without runtime dependencies for the calculator.

~~~bash
python truelove_witts.py single --stools-per-day 8 --blood visible \
  --pulse-bpm 105 --temperature-c 38.1 --hemoglobin-g-dl 10.0 \
  --esr-mm-h 45 --crp-mg-l 55

python truelove_witts.py batch -i sample.csv -o results.csv
~~~

For CSV input, headers **stools_per_day, blood, pulse_bpm, temperature_c, hemoglobin_g_dl** are required; **esr_mm_h, crp_mg_l** are optional. Blood values: **none**, **small**, or **visible**. The example file [sample.csv](sample.csv) uses deidentified cases. Invalid observations cause explicit errors rather than fallback scores. Batch processing does not transmit records and escapes spreadsheet-formula-leading cells in exports.

The Python functions are **assess_truelove_witts(...)**, **calculate_metrics(...)** (compatibility name), and **process_batch(...)**.

## Optional API and legacy modules

The FastAPI service provides **POST /api/severity** for the clinical assessment, and **GET /health**. Install dependencies and run it locally:

~~~bash
python -m pip install fastapi uvicorn pydantic
python cli.py serve
~~~

The separate **cli.py audit/chat/batch**, **agents/**, **enrichment.py**, and **simulator.py** preserve older generic demonstration workflows. These are **not implementations or clinical validation of Truelove–Witts**. The demo chat uses mock responses; it does not provide real clinical reasoning. The optional audit process records metadata in memory, not a durable certified clinical audit. Regex-based identifier detection is incomplete and **must not be treated as guaranteed deidentification**. Do not submit real patient identifiers to the demo endpoints. Set **AUDIT_SECRET_KEY** before using the optional audit service where tamper detection must persist across restarts.

The Dockerfile and Compose file run the optional API service and are not required for the browser calculator.

## Tests

~~~bash
python -m pip install pytest fastapi uvicorn pydantic
python -m pytest -q
node --test web/criteria.test.mjs
~~~

GitHub Actions also compiles Python, tests Python 3.10–3.12, verifies browser rules, and builds the Docker image.

## Compatibility and privacy

The browser app uses native ECMAScript modules and works in current Chrome, Firefox, Safari, and Edge versions that support them; no Pyodide is loaded. Browser output is calculated locally and is not sent to a backend. The optional API processes submitted data server-side and should not be exposed to the public internet without authentication and deployment security controls.

## License

[MIT](LICENSE).

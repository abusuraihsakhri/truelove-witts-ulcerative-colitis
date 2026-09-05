# Truelove Witts Ulcerative Colitis

> **Domain:** Gastroenterology, Hepatology & Clinical Nutrition
> **Reference Guidelines & Standards:** `AASLD & ACG Clinical Practice Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Truelove and Witts Severity Criteria for Ulcerative Colitis
Classifies acute severe ulcerative colitis flares into Mild, Moderate, or Severe.

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_metrics()`**: Core domain algorithm that computes a weighted score from input parameters and classifies severity.
- **`process_single()`** — Evaluates a single case with provided parameters.
- **`process_batch()`** — Processes CSV files with multiple records.
- **`main()`** — CLI entry point for single and batch operations.

### 🏗️ Architecture

| Module | Description |
|:-------|:------------|
| `truelove_witts.py` | Core algorithm (zero-dependency) |
| `cli.py` | Enterprise CLI with audit, chat, batch, and serve commands |
| `agents/` | Multi-agent supervisor, workers, PHI guard, and audit trail |
| `enrichment.py` | Enrichment engines for longitudinal tracking, EHR/FHIR, dashboards, etc. |
| `simulator.py` | High-throughput stress testing simulator |
| `web/index.html` | Operations console dashboard |

---

## 📐 Algorithm

The scoring algorithm computes a weighted sum of numeric inputs:

```text
score = primary_val + Σ(secondary_val_i * (1.0 / i))  for i = 2..n
```

Classification tiers:
- **Low / Standard** (score < 10.0): Standard monitoring
- **Moderate / Intermediate** (10.0 ≤ score < 25.0): Close observation
- **High / Severe** (score ≥ 25.0): Urgent clinical intervention

---

## 💻 CLI Quickstart & Usage

### 1. Single Case Evaluation
```bash
python truelove_witts.py single --v1 14.5 --v2 4.2 --v3 1.8
```

### 2. Batch CSV Processing
```bash
python truelove_witts.py batch -i sample.csv -o results.csv
```

### 3. Enterprise CLI (requires fastapi, uvicorn, pydantic)
```bash
# Audit a single task
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2

# Batch process
python cli.py batch -i sample.csv -o results.csv

# Verify audit trail integrity
python cli.py verify-audit

# Launch REST API server
python cli.py serve --host 127.0.0.1 --port 8000
```

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Patient identifier | Required |
| `v1` | Primary measurement | Required |
| `v2` | Secondary measurement | Required |
| `v3` | Tertiary measurement | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment variable for production deployments:

```bash
# Linux/macOS
export AUDIT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Windows PowerShell
$env:AUDIT_SECRET_KEY = -join ((1..32 | ForEach-Object { Get-Random -Max 16 }).ForEach({ "{0:x}" -f $_ }))
```

---

## 🧪 Testing & Verification

Install test dependencies:

```bash
pip install pytest fastapi uvicorn pydantic
```

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

Build and run with Docker:

```bash
docker build -t truelove-witts-ulcerative-colitis .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key truelove-witts-ulcerative-colitis
```

Or use Docker Compose:

```bash
# Create a .env file with your secret
echo "AUDIT_SECRET_KEY=your-secret-key" > .env
docker-compose up -d
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

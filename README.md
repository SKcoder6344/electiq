# 🗳️ ElectIQ — Predictive Electoral Analytics Matrix

> **CYBERJOAR AI Assignment | PS5 | OC.41335.2026.59218**  
> A data-driven political strategy tool that scores candidates across 6 OSINT-informed factors and forecasts Probability of Win using a weighted softmax model.

[![CI](https://github.com/SKcoder6344/electiq/actions/workflows/ci.yml/badge.svg)](https://github.com/SKcoder6344/electiq/actions)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Plotly](https://img.shields.io/badge/Plotly-5.22-purple)

---

## 🔍 What It Does

Traditional political analysis relies on gut feeling and siloed data. **ElectIQ** quantifies the election into a structured head-to-head matrix:

- Enter 2–4 candidates with their scores across 6 key factors
- Adjust **factor weights** based on the constituency's historical voting behaviour
- Instantly see **Probability of Win**, **radar chart comparisons**, and **strategic gap analysis**
- Export the full matrix as CSV for offline analysis

---

## 🏗️ Architecture

```
User Input (Streamlit UI)
    │
    ▼
Candidate Entry Form  →  utils/validators.py  (input guard)
    │
    ▼
utils/scoring.py
  ├── compute_scores()   Raw score × weight → weighted score per factor
  └── compute_pow()      Softmax normalization → PoW % (sums to 100%)
    │
    ▼
utils/visualizer.py
  ├── render_pow_bar()    Horizontal bar chart
  ├── render_radar_chart() Spider/polar comparison
  └── render_matrix_table() Full DataFrame export
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| App | Streamlit | Rapid deployment, shareable link |
| Charts | Plotly | Interactive radar + bar charts |
| Math | Python stdlib (math.exp) | Softmax, no heavy ML dependency needed |
| Data | Pandas | Matrix table + CSV export |
| CI/CD | GitHub Actions | Auto-test on every push |

---

## 🚀 Quick Start

```bash
git clone https://github.com/SKcoder6344/electiq
cd electiq
pip install -r requirements.txt
streamlit run app.py
```

Or via Docker:
```bash
docker build -t electiq . && docker run -p 8501:8501 electiq
```

---

## 📁 Folder Structure

```
electoral-matrix/
├── app.py                    # Main Streamlit app
├── utils/
│   ├── scoring.py            # Weighted score + PoW engine
│   ├── visualizer.py         # Plotly chart builders
│   └── validators.py         # Input validation
├── tests/
│   └── test_scoring.py       # 11 unit tests
├── .streamlit/config.toml
├── .github/workflows/ci.yml
├── Dockerfile
├── Makefile
└── requirements.txt
```

---

## 🎯 Key Logic (For Submission Email)

ElectIQ solves the **subjective forecasting problem** through three mechanisms:

1. **Weighted Factor Matrix**: Each candidate is scored 1–10 across 6 OSINT-informed factors (Incumbency, Party Strength, Past Work, Personal Base, Caste/Religious Base, Digital Sentiment). An analyst-controlled weight slider (0.5×–3.0×) adjusts each factor's importance based on constituency-specific historical voting behaviour — for example, caste base may deserve a 3× weight in a caste-polarised seat while digital sentiment gets 0.5× in a rural constituency.

2. **Softmax Probability Model**: Rather than simple percentage ranking, PoW is computed via temperature-scaled softmax over total weighted scores. This ensures all probabilities sum to exactly 100%, models diminishing returns (a candidate can't exceed realistic win probabilities), and the temperature parameter controls how decisive vs. spread-out the forecast is.

3. **Strategic Gap Analysis**: Beyond the winner prediction, the dashboard surfaces each candidate's strongest and weakest factor — enabling campaign teams to identify attack vectors against opponents and reinforce their own gaps before election day.

---

## 🔮 Future Improvements

- Live OSINT feed integration (Twitter/X sentiment API, Google Trends)
- Constituency database with historical voting data for auto-weight calibration  
- Swing voter sensitivity analysis — "what if sentiment shifts +2 points?"
- Multi-constituency comparison view

---

## 👤 Author

**Sujal Kumar Nayak**  
B.Tech CSE Final Year | LPU  
GitHub: [@SKcoder6344](https://github.com/SKcoder6344)

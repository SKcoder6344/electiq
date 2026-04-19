"""
CYBERJOAR AI - PS5: Predictive Electoral Analytics Matrix
Author: Sujal Kumar Nayak
"""

import streamlit as st
import pandas as pd
import json
import logging
from utils.scoring import compute_scores, compute_pow
from utils.visualizer import render_radar_chart, render_pow_bar, render_matrix_table
from utils.validators import validate_candidate

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ElectIQ | Electoral Analytics",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #08080f; color: #d0d0e8; }
    .stSidebar { background-color: #0d0d1a !important; }
    .stSidebar label, .stSidebar .stMarkdown { color: #8888cc !important; }

    .main-header {
        background: linear-gradient(135deg, #0d0d2b 0%, #12122a 100%);
        border: 1px solid #2a2a6a;
        border-radius: 8px;
        padding: 20px 30px;
        margin-bottom: 20px;
    }
    .main-header h1 { color: #7b68ee; font-size: 1.8rem; margin: 0; letter-spacing: 3px; }
    .main-header p  { color: #6666aa; margin: 4px 0 0 0; font-size: 0.82rem; letter-spacing: 1px; }

    .stat-card {
        background: #0d0d2b;
        border: 1px solid #2a2a6a;
        border-radius: 6px;
        padding: 14px 18px;
        text-align: center;
        margin-bottom: 8px;
    }
    .stat-card .val { font-size: 2rem; font-weight: 700; color: #7b68ee; }
    .stat-card .lbl { font-size: 0.68rem; color: #6666aa; letter-spacing: 2px; text-transform: uppercase; }

    .section-header {
        color: #7b68ee;
        font-size: 0.72rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        border-bottom: 1px solid #2a2a6a;
        padding-bottom: 6px;
        margin: 16px 0 10px 0;
    }

    .candidate-card {
        background: #0d0d2b;
        border: 1px solid #2a2a6a;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .candidate-card h4 { color: #7b68ee; margin: 0 0 10px 0; font-size: 0.9rem; letter-spacing: 2px; }

    .pow-winner {
        background: linear-gradient(135deg, #1a1a4a, #0d2b1a);
        border: 2px solid #7b68ee;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        margin: 12px 0;
    }
    .pow-winner .win-label { font-size: 0.7rem; letter-spacing: 3px; color: #8888cc; }
    .pow-winner .win-name  { font-size: 1.6rem; font-weight: 700; color: #ffffff; margin: 8px 0 4px 0; }
    .pow-winner .win-pow   { font-size: 1.1rem; color: #7b68ee; }

    .factor-tag {
        display: inline-block;
        background: #1a1a3a;
        border: 1px solid #3a3a7a;
        color: #9999dd;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 0.7rem;
        margin: 2px;
    }

    .stButton > button {
        background: #0d0d2b;
        border: 1px solid #7b68ee;
        color: #7b68ee;
        border-radius: 4px;
        letter-spacing: 1px;
        font-size: 0.8rem;
    }
    .stButton > button:hover { background: #1a1a4a; }
    .stSlider > div > div > div { background: #7b68ee !important; }

    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
MATRIX_FACTORS = [
    "incumbency_effect",
    "party_strength",
    "past_work_record",
    "personal_base",
    "religious_caste_base",
    "digital_sentiment",
]

FACTOR_LABELS = {
    "incumbency_effect":   "Incumbency Effect",
    "party_strength":      "Party Strength",
    "past_work_record":    "Past Work Record",
    "personal_base":       "Personal Base",
    "religious_caste_base":"Religious / Caste Base",
    "digital_sentiment":   "Digital Sentiment",
}

FACTOR_HELP = {
    "incumbency_effect":   "Positive if sitting MLA/MP with good reputation; negative if anti-incumbency wave",
    "party_strength":      "National party strength in this constituency based on past vote share",
    "past_work_record":    "Verified development projects, fund utilization, legislative activity (OSINT)",
    "personal_base":       "Candidate's personal loyalty base independent of party affiliation",
    "religious_caste_base":"Strength of community/caste vote bank alignment in this constituency",
    "digital_sentiment":   "Social media sentiment, news coverage, search trends (OSINT monitoring)",
}

CANDIDATE_COLORS = ["#7b68ee", "#39ff14", "#ff6b39", "#ffcc00"]

# ── Session State ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "candidates":    [],
        "weights":       {f: 1.0 for f in MATRIX_FACTORS},
        "constituency":  "New Delhi",
        "results_ready": False,
        "scores":        {},
        "pow":           {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🗳️ ELECTIQ</h1>
    <p>PREDICTIVE ELECTORAL ANALYTICS MATRIX &nbsp;|&nbsp; CYBERJOAR AI OC.41335.2026.59218</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar — Constituency + Weights ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">📍 CONSTITUENCY</div>', unsafe_allow_html=True)
    st.session_state.constituency = st.text_input(
        "Constituency Name", value=st.session_state.constituency, label_visibility="collapsed"
    )

    st.divider()
    st.markdown('<div class="section-header">⚖️ FACTOR WEIGHTS</div>', unsafe_allow_html=True)
    st.caption("Adjust based on constituency's historical voting behaviour")

    for factor in MATRIX_FACTORS:
        st.session_state.weights[factor] = st.slider(
            FACTOR_LABELS[factor],
            min_value=0.5,
            max_value=3.0,
            value=st.session_state.weights[factor],
            step=0.5,
            help=FACTOR_HELP[factor],
        )

    st.divider()
    st.markdown('<div class="section-header">⚡ QUICK DEMO</div>', unsafe_allow_html=True)
    if st.button("Load Sample Election (Delhi)", use_container_width=True):
        st.session_state.candidates = [
            {
                "name": "Arvind Sharma",
                "party": "National Alliance Party",
                "type": "Incumbent",
                "incumbency_effect":    6,
                "party_strength":       7,
                "past_work_record":     5,
                "personal_base":        6,
                "religious_caste_base": 5,
                "digital_sentiment":    4,
            },
            {
                "name": "Priya Mehta",
                "party": "Progressive Front",
                "type": "Challenger",
                "incumbency_effect":    0,
                "party_strength":       8,
                "past_work_record":     7,
                "personal_base":        8,
                "religious_caste_base": 6,
                "digital_sentiment":    9,
            },
            {
                "name": "Ramesh Yadav",
                "party": "Regional Block",
                "type": "Challenger",
                "incumbency_effect":    0,
                "party_strength":       6,
                "past_work_record":     6,
                "personal_base":        7,
                "religious_caste_base": 9,
                "digital_sentiment":    5,
            },
            {
                "name": "Sunita Rawat",
                "party": "Independent",
                "type": "Independent",
                "incumbency_effect":    0,
                "party_strength":       2,
                "past_work_record":     4,
                "personal_base":        5,
                "religious_caste_base": 3,
                "digital_sentiment":    3,
            },
        ]
        st.session_state.results_ready = False
        st.success("✅ Sample candidates loaded!")
        logger.info("Sample election data loaded")


# ── Main: Candidate Input Panel ───────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="section-header">👤 ADD CANDIDATE</div>', unsafe_allow_html=True)

    with st.form("add_candidate_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            cand_name  = st.text_input("Full Name",  placeholder="e.g. Arvind Sharma")
            cand_party = st.text_input("Party",       placeholder="e.g. National Alliance")
        with c2:
            cand_type  = st.selectbox("Role", ["Incumbent", "Challenger", "Independent"])
            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("**Score each factor (1 = Very Weak → 10 = Very Strong)**")

        factor_scores = {}
        f1, f2 = st.columns(2)
        factors_list = list(MATRIX_FACTORS)

        for i, factor in enumerate(factors_list):
            col = f1 if i % 2 == 0 else f2
            with col:
                # Incumbency: 0 for non-incumbents makes sense
                min_val = 0 if factor == "incumbency_effect" else 1
                factor_scores[factor] = st.slider(
                    FACTOR_LABELS[factor],
                    min_value=min_val,
                    max_value=10,
                    value=5,
                    step=1,
                    help=FACTOR_HELP[factor],
                )

        submitted = st.form_submit_button("➕ Add Candidate", use_container_width=True)

        if submitted:
            candidate = {"name": cand_name, "party": cand_party, "type": cand_type, **factor_scores}
            valid, msg = validate_candidate(candidate)
            if valid:
                if len(st.session_state.candidates) >= 4:
                    st.warning("⚠️ Maximum 4 candidates allowed. Remove one first.")
                else:
                    st.session_state.candidates.append(candidate)
                    st.session_state.results_ready = False
                    st.success(f"✅ {cand_name} added!")
                    logger.info(f"Candidate added: {cand_name} ({cand_party})")
            else:
                st.error(f"❌ {msg}")

with col_right:
    st.markdown('<div class="section-header">📋 CANDIDATE ROSTER</div>', unsafe_allow_html=True)

    if not st.session_state.candidates:
        st.markdown("""
        <div style="border:1px dashed #2a2a6a; border-radius:8px; padding:40px; text-align:center; color:#4a4a8a;">
            <div style="font-size:2rem">🗳️</div>
            <div style="font-size:0.9rem; letter-spacing:2px; margin-top:8px;">NO CANDIDATES ADDED</div>
            <div style="font-size:0.75rem; margin-top:6px; color:#3a3a7a;">Add at least 2 to run analysis</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, cand in enumerate(st.session_state.candidates):
            color = CANDIDATE_COLORS[i % len(CANDIDATE_COLORS)]
            with st.container():
                st.markdown(f"""
                <div class="candidate-card">
                    <h4 style="color:{color}">{'🔴' if cand['type']=='Incumbent' else '🔵'} {cand['name'].upper()}</h4>
                    <div style="font-size:0.8rem; color:#8888cc; margin-bottom:6px;">{cand['party']} &nbsp;·&nbsp; {cand['type']}</div>
                    <div>
                        {''.join(f'<span class="factor-tag">{FACTOR_LABELS[f]}: {cand[f]}</span>' for f in MATRIX_FACTORS)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑 Remove {cand['name']}", key=f"remove_{i}"):
                    st.session_state.candidates.pop(i)
                    st.session_state.results_ready = False
                    st.rerun()

# ── Run Analysis Button ───────────────────────────────────────────────────────
st.divider()

if len(st.session_state.candidates) >= 2:
    if st.button("🔍 RUN ELECTORAL ANALYSIS", use_container_width=True, type="primary"):
        with st.spinner("Computing weighted scores and probability of win..."):
            scores = compute_scores(st.session_state.candidates, st.session_state.weights)
            pow    = compute_pow(scores)
            st.session_state.scores        = scores
            st.session_state.pow           = pow
            st.session_state.results_ready = True
            logger.info(f"Analysis run for {len(st.session_state.candidates)} candidates in {st.session_state.constituency}")
else:
    st.info("ℹ️ Add at least 2 candidates to run the analysis.")


# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.results_ready:
    scores = st.session_state.scores
    pow    = st.session_state.pow

    winner_name = max(pow, key=pow.get)
    winner_pow  = pow[winner_name]

    st.markdown(f'<div class="section-header">📊 ANALYSIS RESULTS — {st.session_state.constituency.upper()}</div>', unsafe_allow_html=True)

    # Winner card
    st.markdown(f"""
    <div class="pow-winner">
        <div class="win-label">◈ PROJECTED WINNER</div>
        <div class="win-name">{winner_name}</div>
        <div class="win-pow">Probability of Win: {winner_pow:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    # Stat cards
    sc1, sc2, sc3, sc4 = st.columns(4)
    stat_cols = [sc1, sc2, sc3, sc4]
    for i, cand in enumerate(st.session_state.candidates):
        name = cand["name"]
        with stat_cols[i]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="val" style="color:{CANDIDATE_COLORS[i]}">{pow[name]:.1f}%</div>
                <div class="lbl">{name}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    tab1, tab2, tab3 = st.tabs(["📊 Probability of Win", "🕸 Factor Comparison", "📋 Full Matrix"])

    with tab1:
        fig_bar = render_pow_bar(pow, CANDIDATE_COLORS)
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        fig_radar = render_radar_chart(
            st.session_state.candidates, MATRIX_FACTORS, FACTOR_LABELS, CANDIDATE_COLORS
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with tab3:
        matrix_df = render_matrix_table(
            st.session_state.candidates, scores, pow, MATRIX_FACTORS, FACTOR_LABELS, st.session_state.weights
        )
        st.dataframe(matrix_df, use_container_width=True, hide_index=True)

        # Download
        csv = matrix_df.to_csv(index=False)
        st.download_button(
            "⬇️ Export Matrix as CSV",
            data=csv,
            file_name=f"electoral_matrix_{st.session_state.constituency.replace(' ','_')}.csv",
            mime="text/csv",
        )

    # Strategic gap analysis
    st.markdown('<div class="section-header">🎯 STRATEGIC GAP ANALYSIS</div>', unsafe_allow_html=True)
    _gap_cols = st.columns(len(st.session_state.candidates))
    for i, cand in enumerate(st.session_state.candidates):
        name = cand["name"]
        raw  = {f: cand[f] for f in MATRIX_FACTORS}
        strongest = max(raw, key=raw.get)
        weakest   = min(raw, key=raw.get)
        with _gap_cols[i]:
            color = CANDIDATE_COLORS[i]
            st.markdown(f"""
            <div class="candidate-card">
                <h4 style="color:{color}">{name}</h4>
                <div style="font-size:0.75rem; color:#8888cc; margin-bottom:4px;">PoW: <b style="color:{color}">{pow[name]:.1f}%</b></div>
                <div style="font-size:0.73rem;">
                    <span style="color:#39ff14">▲ Strength:</span> {FACTOR_LABELS[strongest]} ({raw[strongest]}/10)<br>
                    <span style="color:#ff6b39">▼ Gap:</span> {FACTOR_LABELS[weakest]} ({raw[weakest]}/10)
                </div>
            </div>
            """, unsafe_allow_html=True)

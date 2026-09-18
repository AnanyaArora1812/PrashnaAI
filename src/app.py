"""
PrashnaAI dashboard.

Run:
    streamlit run src/app.py
"""

from __future__ import annotations

from datetime import date, time
import os
from html import escape

import streamlit as st

from astro.geocoding import (
    resolve_place,
    resolve_from_candidate,
    PlaceNotFoundError,
    AmbiguousPlaceError,
)
from astro.chart_calculator import calculate_birth_chart
from astro.numerology import calculate_numerology
from astro.narrative import TOPIC_LABELS
from astro.narrative_groq import generate_topic_narrative_groq, get_groq_client
from astro.transit_calculator import calculate_monthly_transits
from astro.monthly_narrative import generate_monthly_narrative_groq

from rag.retriever import Retriever


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FAISS_INDEX_PATH = "datasets/processed/faiss_index/index.faiss"
FAISS_METADATA_PATH = "datasets/processed/faiss_index/metadata.json"
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


st.set_page_config(
    page_title="PrashnaAI",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# UI styling
#
# IMPORTANT:
# The CSS is rendered with st.html(), not st.markdown().
# This prevents the CSS from appearing as visible text in Streamlit.
# ---------------------------------------------------------------------------

st.html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

    :root {
        --paper: #f8f4ef;
        --paper-2: #fffaf5;
        --white: #fffdfb;
        --ink: #202c43;
        --muted: #706f78;
        --soft: #99939a;
        --line: #e9dfd7;
        --line-strong: #daccc1;
        --gold: #c58a3a;
        --gold-dark: #9b6726;
        --peach: #efb49e;
        --rose: #df91a2;
        --lavender: #b8a9df;
        --sky: #9fc7df;
        --sage: #a8c7b5;
        --plum: #7466a8;
        --shadow: 0 16px 45px rgba(49, 42, 56, .075);
        --serif: 'Playfair Display', Georgia, serif;
        --sans: 'DM Sans', system-ui, sans-serif;
    }

    .stApp {
        color: var(--ink);
        background-color: #fbf7f2;
        background-image:
            radial-gradient(circle at 7% 9%, rgba(255,176,102,.34) 0, rgba(255,176,102,0) 20%),
            radial-gradient(circle at 91% 10%, rgba(203,174,255,.30) 0, rgba(203,174,255,0) 23%),
            radial-gradient(circle at 92% 88%, rgba(117,211,204,.22) 0, rgba(117,211,204,0) 21%),
            radial-gradient(circle at 9% 87%, rgba(255,145,170,.22) 0, rgba(255,145,170,0) 20%),
            radial-gradient(circle at 50% 44%, rgba(255,255,255,.92) 0, rgba(255,255,255,0) 47%),
            repeating-radial-gradient(circle at 50% 50%, rgba(137,91,184,.045) 0 1px, transparent 1px 48px);
        background-attachment: fixed;
        min-height: 100vh;
    }

    /* Celestial background artwork — decorative only, never blocks clicks. */
    .stApp::before {
        content: '♈   ♉   ♊   ♋   ♌   ♍   ♎   ♏   ♐   ♑   ♒   ♓';
        position: fixed;
        left: 50%;
        top: 0.7rem;
        transform: translateX(-50%);
        width: 112vw;
        height: 82px;
        text-align: center;
        white-space: nowrap;
        font-family: Georgia, serif;
        font-size: clamp(1.35rem, 2.5vw, 2.15rem);
        letter-spacing: .34em;
        color: rgba(112,82,167,.20);
        text-shadow: 0 2px 14px rgba(196,144,61,.10);
        pointer-events: none;
        z-index: 0;
    }

    .stApp::after {
        content: '☉   ☾   ✦   ☿   ♀   ♂   ♃   ♄   ✦   ☽';
        position: fixed;
        right: -7rem;
        bottom: 1.5rem;
        width: 58vw;
        height: 270px;
        padding-top: 92px;
        text-align: center;
        border: 2px solid rgba(194,139,54,.13);
        border-radius: 50%;
        box-shadow: 0 0 0 18px rgba(194,139,54,.025), 0 0 0 42px rgba(112,82,167,.025);
        transform: rotate(-11deg);
        font-family: Georgia, serif;
        font-size: 1.45rem;
        letter-spacing: .45em;
        color: rgba(194,139,54,.19);
        text-shadow: 0 0 16px rgba(194,139,54,.10);
        pointer-events: none;
        z-index: 0;
    }

    /* Extra corner zodiac constellations. */
    body::before {
        content: '✦   ·   ✧     ♓   ·   ✦';
        position: fixed;
        left: 1.5rem;
        bottom: 7rem;
        font-family: Georgia, serif;
        font-size: 1.55rem;
        letter-spacing: .28em;
        color: rgba(224,113,139,.20);
        pointer-events: none;
        z-index: 0;
    }

    body::after {
        content: '✧   ♌   ·   ✦   ♐';
        position: fixed;
        right: 1.2rem;
        top: 8.5rem;
        font-family: Georgia, serif;
        font-size: 1.55rem;
        letter-spacing: .25em;
        color: rgba(63,160,154,.19);
        transform: rotate(8deg);
        pointer-events: none;
        z-index: 0;
    }

    /* Fine zodiac-wheel geometry in the page background. */
    [data-testid='stAppViewContainer']::before {
        content: '';
        position: fixed;
        left: -155px;
        top: 34%;
        width: 310px;
        height: 310px;
        border: 1px solid rgba(112,82,167,.10);
        border-radius: 50%;
        box-shadow: inset 0 0 0 22px rgba(112,82,167,.018), inset 0 0 0 23px rgba(194,139,54,.09), inset 0 0 0 68px rgba(194,139,54,.018);
        pointer-events: none;
        z-index: 0;
    }

    .block-container {
        max-width: 1360px;
        padding-top: 1.55rem;
        padding-bottom: 4rem;
        position: relative;
        z-index: 1;
    }

    html, body, [class*='css'] { font-family: var(--sans); }
    h1,h2,h3,h4 { font-family: var(--serif); color: var(--ink); }

    /* ---------- Topbar / hero ---------- */
    .pa-topbar {
        display:flex; align-items:center; justify-content:space-between;
        padding:.15rem 0 1rem;
    }
    .pa-brandmark {
        display:flex; align-items:center; gap:.7rem;
        font-family:var(--serif); font-size:1.2rem; font-weight:700;
        letter-spacing:-.02em; color:var(--ink);
    }
    .pa-orbit {
        width:38px;height:38px;border:1px solid rgba(197,138,58,.35);border-radius:50%;
        display:grid;place-items:center;background:linear-gradient(135deg,#fff9ef,#f4eafa);
        position:relative;box-shadow:0 5px 18px rgba(100,80,50,.08);
    }
    .pa-orbit::before { content:'☽';font-size:1.05rem;color:var(--gold); }
    .pa-topnote { color:var(--muted);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase; }

    .pa-hero {
        position:relative;overflow:hidden;padding:2.55rem 2.6rem 2.45rem;
        border:1px solid rgba(218,204,193,.85);border-radius:28px;
        background:
            radial-gradient(circle at 83% 25%, rgba(184,169,223,.36), transparent 25%),
            radial-gradient(circle at 72% 95%, rgba(239,180,158,.25), transparent 27%),
            linear-gradient(115deg, rgba(255,253,251,.98), rgba(255,248,241,.90));
        box-shadow:var(--shadow);
    }
    .pa-hero::before {
        content:'☉'; position:absolute; right:6%; top:-50px;
        width:220px;height:220px;border:1px solid rgba(197,138,58,.18);border-radius:50%;
        display:grid;place-items:center;font-family:Georgia,serif;font-size:5.5rem;
        color:rgba(197,138,58,.18);
        box-shadow:0 0 0 18px rgba(197,138,58,.025),0 0 0 38px rgba(116,102,168,.025);
        pointer-events:none;
    }
    .pa-hero::after {
        content:'♈  ♉  ♊  ♋  ♌  ♍  ♎  ♏  ♐  ♑  ♒  ♓';
        position:absolute;right:2%;bottom:1rem;font-family:Georgia,serif;
        font-size:.72rem;letter-spacing:.32em;color:rgba(116,102,168,.15);pointer-events:none;
    }
    .pa-eyebrow {
        display:inline-flex;align-items:center;gap:.5rem;font-size:.68rem;font-weight:700;
        letter-spacing:.17em;text-transform:uppercase;color:var(--plum);margin-bottom:.65rem;
    }
    .pa-eyebrow::before { content:'✦'; font-size:.7rem; color:var(--gold); }
    .pa-title {
        font-family:var(--serif);font-size:clamp(2.5rem,5vw,4.45rem);line-height:1;
        font-weight:600;letter-spacing:-.045em;margin:0;color:var(--ink);
    }
    .pa-subtitle { max-width:730px;font-size:.94rem;line-height:1.75;color:var(--muted);margin-top:.9rem; }
    .pa-meta-row { display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.1rem; }
    .pa-chip {
        display:inline-flex;align-items:center;gap:.35rem;border:1px solid rgba(218,204,193,.95);
        border-radius:999px;background:rgba(255,255,255,.68);padding:.34rem .72rem;
        color:#665f68;font-size:.7rem;font-weight:600;box-shadow:0 3px 10px rgba(60,45,45,.025);
    }

    /* ---------- Sidebar ---------- */
    [data-testid='stSidebar'] {
        background:
            radial-gradient(circle at 20% 5%, rgba(239,180,158,.26), transparent 28%),
            radial-gradient(circle at 90% 65%, rgba(184,169,223,.20), transparent 30%),
            #f6f0ea;
        border-right:1px solid var(--line);
    }
    [data-testid='stSidebar']::before {
        content:'☽  ✦  ☉';position:absolute;right:1.2rem;top:1rem;
        font-family:Georgia,serif;font-size:1rem;color:rgba(197,138,58,.20);letter-spacing:.35em;
    }
    [data-testid='stSidebar'] > div:first-child { padding:1.15rem .9rem 1.5rem; }
    .pa-side-brand { font-family:var(--serif);font-size:1.6rem;font-weight:700;letter-spacing:-.03em;color:var(--ink); }
    .pa-side-kicker { font-size:.7rem;color:var(--muted);line-height:1.55;margin:.15rem 0 1.15rem; }
    .pa-side-section {
        display:flex;align-items:center;gap:.45rem;font-size:.68rem;font-weight:700;
        letter-spacing:.12em;text-transform:uppercase;color:var(--plum);margin:1rem 0 .6rem;
    }
    .pa-side-section::before { content:'✦';font-size:.55rem;color:var(--gold); }
    .pa-side-note { font-size:.73rem;line-height:1.55;color:var(--muted);margin-bottom:.9rem; }
    [data-testid='stSidebar'] .stForm {
        border:1px solid rgba(218,204,193,.9);border-radius:20px;padding:.9rem .82rem .8rem;
        background:rgba(255,253,251,.76);box-shadow:0 10px 30px rgba(70,52,45,.055);
    }
    [data-testid='stSidebar'] label { font-size:.73rem;font-weight:600;color:#625d66; }
    [data-testid='stSidebar'] input, [data-testid='stSidebar'] textarea,
    [data-testid='stSidebar'] [data-baseweb='select'] > div { border-radius:11px; }
    .pa-side-orbit {
        margin-top:1rem;padding:1rem;border:1px solid rgba(218,204,193,.85);border-radius:20px;
        background:linear-gradient(135deg,rgba(255,253,251,.78),rgba(246,237,250,.65));text-align:center;
    }
    .pa-zodiac-line { font-family:Georgia,serif;font-size:1.35rem;letter-spacing:.18em;color:#8775ad;line-height:1.7; }
    .pa-side-orbit-note { font-size:.66rem;color:var(--soft);margin-top:.25rem; }
    .pa-side-mini { display:grid;grid-template-columns:1fr 1fr;gap:.5rem;margin-top:.7rem; }
    .pa-mini { padding:.65rem;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.62); }
    .pa-mini-label { font-size:.58rem;text-transform:uppercase;letter-spacing:.08em;color:var(--soft);font-weight:700; }
    .pa-mini-value { font-family:var(--serif);font-size:1.05rem;margin-top:.15rem;color:var(--ink); }

    /* ---------- Buttons ---------- */
    .stButton > button, [data-testid='stFormSubmitButton'] button {
        border-radius:12px;min-height:2.65rem;border:1px solid var(--gold);
        background:linear-gradient(135deg,#c99246,#a96f2b);color:#fffdf9;font-weight:700;
        box-shadow:0 7px 18px rgba(166,108,40,.18);transition:all .18s ease;
    }
    .stButton > button:hover, [data-testid='stFormSubmitButton'] button:hover {
        background:linear-gradient(135deg,#b97c34,#945d20);border-color:#945d20;transform:translateY(-1px);
        box-shadow:0 10px 22px rgba(166,108,40,.23);
    }

    /* ---------- Dashboard intro ---------- */
    .pa-welcome { display:grid;grid-template-columns:1.25fr .75fr;gap:1rem;margin:1.2rem 0 1rem; }
    .pa-welcome-card {
        min-height:155px;padding:1.35rem 1.45rem;border:1px solid var(--line);border-radius:20px;
        background:linear-gradient(135deg,rgba(255,253,251,.92),rgba(251,243,237,.83));box-shadow:var(--shadow);position:relative;overflow:hidden;
    }
    .pa-welcome-card:first-child { background:linear-gradient(135deg,rgba(255,253,251,.96),rgba(245,238,250,.72)); }
    .pa-welcome-card::after { content:'♐';position:absolute;right:1rem;bottom:-1rem;font-family:Georgia,serif;font-size:6rem;color:rgba(116,102,168,.09); }
    .pa-welcome-kicker { font-size:.64rem;font-weight:700;text-transform:uppercase;letter-spacing:.13em;color:var(--plum); }
    .pa-welcome-title { font-family:var(--serif);font-size:1.45rem;margin:.35rem 0 .3rem;color:var(--ink); }
    .pa-welcome-text { max-width:650px;font-size:.78rem;line-height:1.65;color:var(--muted); }
    .pa-symbol-panel { display:grid;place-items:center;text-align:center;background:linear-gradient(135deg,#fff9ef,#f1eafa); }
    .pa-symbol-ring {
        width:106px;height:106px;border:1px solid rgba(197,138,58,.35);border-radius:50%;display:grid;place-items:center;
        box-shadow:inset 0 0 0 10px rgba(197,138,58,.035),inset 0 0 0 24px rgba(116,102,168,.035);
        font-family:Georgia,serif;color:var(--gold);font-size:2.1rem;
    }
    .pa-symbol-caption { font-size:.67rem;color:var(--soft);margin-top:.55rem; }

    /* ---------- Fact ribbon ---------- */
    .pa-ribbon {
        display:grid;grid-template-columns:repeat(5,1fr);background:rgba(255,253,251,.92);
        border:1px solid var(--line);border-radius:20px;overflow:hidden;box-shadow:var(--shadow);margin:.75rem 0 1.65rem;
    }
    .pa-fact { padding:1rem 1.05rem;border-right:1px solid var(--line);position:relative; }
    .pa-fact:last-child { border-right:none; }
    .pa-fact::before { content:'✦';position:absolute;top:.55rem;right:.65rem;color:rgba(197,138,58,.45);font-size:.65rem; }
    .pa-fact-label { font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--soft);margin-bottom:.28rem; }
    .pa-fact-value { font-family:var(--serif);font-size:1.12rem;line-height:1.25;color:var(--ink); }
    .pa-fact-value.pa-num { color:var(--plum);font-weight:700; }
    .pa-hi { display:block;margin-top:.15rem;font-size:.64rem;color:var(--muted); }

    /* ---------- Tabs / sections ---------- */
    .stTabs [data-baseweb='tab-list'] { gap:1.7rem;border-bottom:1px solid var(--line); }
    .stTabs [data-baseweb='tab'] { font-size:.8rem;font-weight:700;color:var(--muted);padding:.72rem .05rem; }
    .stTabs [aria-selected='true'] { color:var(--plum); }
    .stTabs [data-baseweb='tab-highlight'] { background:linear-gradient(90deg,var(--gold),var(--plum));height:3px;border-radius:3px; }
    .pa-section { font-family:var(--serif);font-size:1.5rem;font-weight:600;color:var(--ink);margin:.45rem 0 .2rem; }
    .pa-section-note { max-width:800px;color:var(--muted);font-size:.78rem;line-height:1.65;margin-bottom:1rem; }

    /* ---------- Cards ---------- */
    .pa-card {
        background:linear-gradient(145deg,rgba(255,253,251,.94),rgba(250,244,240,.82));
        border:1px solid var(--line);border-radius:18px;padding:1.15rem 1.2rem;
        box-shadow:var(--shadow);height:100%;position:relative;overflow:hidden;
    }
    .pa-card::before { content:'';position:absolute;left:0;top:0;width:100%;height:3px;background:linear-gradient(90deg,var(--peach),var(--lavender),var(--sky));opacity:.75; }
    .pa-card::after { content:'✦';position:absolute;right:.9rem;top:.65rem;color:rgba(116,102,168,.25);font-size:.8rem; }
    .pa-card-label { font-size:.61rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--plum); }
    .pa-card-value { font-family:var(--serif);font-size:1.3rem;color:var(--ink);margin-top:.3rem; }
    .pa-card-note { font-size:.7rem;color:var(--muted);margin-top:.25rem;line-height:1.55; }
    .pa-reading {
        max-width:82ch;font-family:var(--serif);font-size:.98rem;line-height:1.82;color:#393b43;
        background:linear-gradient(90deg,rgba(247,239,249,.72),rgba(255,253,251,.62));
        border-left:3px solid var(--plum);padding:.35rem 0 .35rem 1.15rem;border-radius:0 12px 12px 0;
    }
    .pa-reading p { margin-bottom:1rem; }
    .pa-ingress { padding:.7rem .85rem;margin:.6rem 0 1rem;border-left:3px solid var(--sage);background:#eef6f1;color:#5d7466;font-size:.78rem;line-height:1.55;border-radius:0 10px 10px 0; }
    .pa-flag { padding:.7rem .85rem;margin:.7rem 0;border-left:3px solid var(--rose);background:#fbecf0;color:#875b67;font-size:.8rem;line-height:1.55;border-radius:0 10px 10px 0; }

    /* ---------- Streamlit inputs / data ---------- */
    [data-testid='stDataFrame'] { border:1px solid var(--line);border-radius:14px;overflow:hidden;box-shadow:var(--shadow); }
    [data-testid='stExpander'] details { background:rgba(255,253,251,.90);border:1px solid var(--line);border-radius:15px;box-shadow:none;margin-bottom:.55rem; }
    [data-testid='stExpander'] summary { font-weight:700;color:var(--ink); }
    .stAlert { border-radius:12px; }
    [data-testid='stProgressBar'] > div > div { background:linear-gradient(90deg,var(--gold),var(--plum)); }

    /* ---------- Empty state ---------- */
    .pa-empty {
        margin-top:1.2rem;padding:4.2rem 2rem;text-align:center;background:rgba(255,253,251,.84);
        border:1px solid var(--line);border-radius:26px;box-shadow:var(--shadow);position:relative;overflow:hidden;
    }
    .pa-empty::before {
        content:'☽  ✦  ♈  ♉  ♊  ♋  ♌  ♍  ♎  ♏  ♐  ♑  ♒  ♓  ✦  ☉';
        position:absolute;top:1rem;left:50%;transform:translateX(-50%);font-family:Georgia,serif;
        letter-spacing:.24em;color:rgba(116,102,168,.14);white-space:nowrap;
    }
    .pa-empty::after {
        content:'✦    NUMEROLOGY    ✦    PLANETS    ✦    DESTINY    ✦';
        position:absolute;bottom:1rem;left:50%;transform:translateX(-50%);font-family:Georgia,serif;
        font-size:.62rem;letter-spacing:.18em;color:rgba(197,138,58,.16);white-space:nowrap;
    }
    .pa-empty-icon { font-family:Georgia,serif;font-size:2.8rem;color:var(--gold);margin-bottom:.9rem; }
    .pa-empty-title { font-family:var(--serif);font-size:1.8rem;color:var(--ink);margin-bottom:.55rem; }
    .pa-empty-text { max-width:620px;margin:auto;color:var(--muted);line-height:1.75;font-size:.82rem; }

    .pa-compat-score {
        background: radial-gradient(circle at 50% 15%, rgba(197,138,58,.25), transparent 38%), linear-gradient(145deg,#20233a,#352d50);
        color:#fffaf2;border-radius:24px;padding:1.6rem;text-align:center;box-shadow:0 18px 40px rgba(44,36,63,.18);
    }
    .pa-compat-number { font-family:var(--serif);font-size:3.5rem;line-height:1;font-weight:700;color:#f6d79f; }
    .pa-compat-label { margin-top:.45rem;font-size:.72rem;letter-spacing:.13em;text-transform:uppercase;color:#eadfd1; }
    .pa-advice-do,.pa-advice-dont { padding:1.1rem 1.2rem;border-radius:18px;border:1px solid var(--line);line-height:1.65;font-size:.8rem;height:100%; }
    .pa-advice-do { background:linear-gradient(145deg,#eef7f0,#fbfdf9); }
    .pa-advice-dont { background:linear-gradient(145deg,#fbf0f2,#fffaf9); }
    .pa-advice-do li,.pa-advice-dont li { margin:.45rem 0; }

    .pa-footer {
        margin-top:3rem;padding:1.1rem 0;border-top:1px solid var(--line);color:var(--soft);
        font-size:.65rem;text-align:center;letter-spacing:.08em;
    }

    @media (max-width:900px) {
        .pa-welcome { grid-template-columns:1fr; }
        .pa-ribbon { grid-template-columns:repeat(2,1fr); }
        .pa-fact:nth-child(2), .pa-fact:nth-child(4) { border-right:none; }
        .pa-fact:nth-child(-n+3) { border-bottom:1px solid var(--line); }
        .pa-hero { padding:1.8rem 1.35rem; }
        .stApp::after { display:none; }
    }
    </style>
    """
)



# ---------------------------------------------------------------------------
# Cached resources
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Loading retrieval index...")
def load_retriever() -> Retriever:
    return Retriever(
        index_path=FAISS_INDEX_PATH,
        metadata_path=FAISS_METADATA_PATH,
        embedding_model_name=EMBEDDING_MODEL_NAME,
    )


@st.cache_resource(show_spinner="Connecting to Groq...")
def load_groq_client():
    return get_groq_client()


def _stretch() -> dict:
    try:
        major, minor = (int(x) for x in st.__version__.split(".")[:2])
    except Exception:
        return {"use_container_width": True}

    return (
        {"width": "stretch"}
        if (major, minor) >= (1, 49)
        else {"use_container_width": True}
    )


STRETCH = _stretch()


# ---------------------------------------------------------------------------
# AI reading engine
# ---------------------------------------------------------------------------

# Groq retired older Llama production IDs in August 2026. Keep this configurable.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

SIGN_ORDER = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
]
SIGN_ALIASES = {
    "Aries": "Mesha", "Taurus": "Vrishabha", "Gemini": "Mithuna",
    "Cancer": "Karka", "Leo": "Simha", "Virgo": "Kanya",
    "Libra": "Tula", "Scorpio": "Vrishchika", "Sagittarius": "Dhanu",
    "Capricorn": "Makara", "Aquarius": "Kumbha", "Pisces": "Meena",
}
ELEMENTS = {
    "Mesha": "Fire", "Simha": "Fire", "Dhanu": "Fire",
    "Vrishabha": "Earth", "Kanya": "Earth", "Makara": "Earth",
    "Mithuna": "Air", "Tula": "Air", "Kumbha": "Air",
    "Karka": "Water", "Vrishchika": "Water", "Meena": "Water",
}


def _canonical_sign(value: str) -> str:
    return SIGN_ALIASES.get(str(value or "").strip(), str(value or "").strip())


def _sign_distance(a: str, b: str) -> int:
    a = _canonical_sign(a)
    b = _canonical_sign(b)
    if a not in SIGN_ORDER or b not in SIGN_ORDER:
        return 99
    d = abs(SIGN_ORDER.index(a) - SIGN_ORDER.index(b))
    return min(d, 12 - d)


def _planet(chart, name):
    return chart.planets.get(name)


def _chart_context(chart) -> str:
    rows = []
    for planet_name, planet in chart.planets.items():
        rows.append(
            f"{planet_name}: sign={planet.sign}; house={planet.house}; "
            f"nakshatra={getattr(planet, 'nakshatra', '')}; pada={getattr(planet, 'pada', '')}; "
            f"retrograde={getattr(planet, 'retrograde', '')}"
        )
    return (
        f"Name: {chart.name}\n"
        f"Birth place: {chart.place_name}\n"
        f"Ascendant: {chart.ascendant_sign}\n"
        + "\n".join(rows)
    )


def _normalise_chunks(raw):
    if raw is None:
        return []
    if isinstance(raw, dict):
        for key in ("results", "chunks", "documents", "matches"):
            if isinstance(raw.get(key), list):
                raw = raw[key]
                break
        else:
            raw = [raw]
    if not isinstance(raw, (list, tuple)):
        raw = [raw]
    chunks = []
    for item in raw[:6]:
        if isinstance(item, dict):
            meta = item.get("metadata", {}) or {}
            text = item.get("text") or item.get("content") or item.get("page_content") or ""
            source = item.get("source_file") or item.get("source") or meta.get("source", "")
            page = item.get("page_number") or item.get("page") or meta.get("page", "")
            score = item.get("score", item.get("similarity", ""))
        else:
            text = getattr(item, "text", "") or getattr(item, "page_content", "") or str(item)
            source = getattr(item, "source_file", "") or getattr(item, "source", "")
            page = getattr(item, "page_number", "") or getattr(item, "page", "")
            score = getattr(item, "score", "")
        if text:
            chunks.append({"text": str(text), "source_file": str(source), "page_number": str(page), "score": score})
    return chunks


def retrieve_classical_context(retriever, query: str):
    """Adapter for common versions of the project's Retriever API."""
    for method_name in ("search", "retrieve", "query", "get_relevant_documents"):
        fn = getattr(retriever, method_name, None)
        if not callable(fn):
            continue
        for attempt in (
            lambda: fn(query, top_k=6),
            lambda: fn(query, k=6),
            lambda: fn(query, 6),
            lambda: fn(query),
        ):
            try:
                chunks = _normalise_chunks(attempt())
                if chunks:
                    return chunks
            except TypeError:
                continue
            except Exception:
                break
    return []


def _call_groq(client, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.35,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def generate_unique_prediction(chart, topic: str, label: str, retriever, client):
    context_chunks = retrieve_classical_context(
        retriever,
        f"{label} Vedic astrology houses planets outcomes advice Brihat Parashara Hora Shastra",
    )
    source_context = "\n\n".join(
        f"[{c['source_file']} p.{c['page_number']}]\n{c['text']}" for c in context_chunks
    ) or "No classical passage was retrieved; do not invent a citation."
    prompt = f"""Create a highly personalised {label} reading for this birth chart.

CHART
{_chart_context(chart)}

RETRIEVED CLASSICAL CONTEXT
{source_context}

Rules:
- Base every personalised statement on the supplied chart placements.
- Use the retrieved classical context when it actually supports the point.
- Do not invent planetary placements, dates, events, quotations, or citations.
- Do not give generic horoscope filler. Explain WHY a placement changes the reading.
- Make this reading materially different for a different chart.
- Separate chart interpretation from practical advice.
- Avoid deterministic claims such as guaranteed marriage, death, illness, wealth, or exact events.
- Be specific, nuanced, and useful.
- End with 3 practical actions for the user.

Return a polished 5-7 paragraph reading with short section headings."""
    narrative = _call_groq(
        client,
        "You are PrashnaAI's Vedic astrology interpretation engine. You are evidence-grounded, transparent about uncertainty, and never fabricate chart data or source citations.",
        prompt,
        max_tokens=1800,
    )
    return {"narrative": narrative, "retrieved_chunks": context_chunks}


def compatibility_analysis(chart_a, chart_b, num_a, num_b):
    """Traditional-style heuristic, not a scientifically validated probability."""
    score = 50.0
    reasons = []
    moon_a = _planet(chart_a, "Moon")
    moon_b = _planet(chart_b, "Moon")
    venus_a = _planet(chart_a, "Venus")
    venus_b = _planet(chart_b, "Venus")
    mars_a = _planet(chart_a, "Mars")
    mars_b = _planet(chart_b, "Mars")

    if moon_a and moon_b:
        d = _sign_distance(moon_a.sign, moon_b.sign)
        if d in (0, 4, 8):
            score += 14
            reasons.append("Moon-sign relationship is supportive in this heuristic.")
        elif d in (2, 3, 5):
            score += 8
            reasons.append("Moon signs have an adaptable or complementary relationship.")
        elif d == 6:
            score -= 5
            reasons.append("Moon signs are opposite, which can create attraction plus strong differences.")
        else:
            score -= 4

    if venus_a and venus_b:
        sa = _canonical_sign(venus_a.sign)
        sb = _canonical_sign(venus_b.sign)
        ea = ELEMENTS.get(sa)
        eb = ELEMENTS.get(sb)
        if sa == sb:
            score += 8
            reasons.append("Venus signs match, suggesting similar affection styles.")
        elif {ea, eb} in ({"Fire", "Air"}, {"Earth", "Water"}):
            score += 6
            reasons.append("Venus elements can support each other's relationship style.")

    if mars_a and mars_b:
        if _canonical_sign(mars_a.sign) == _canonical_sign(mars_b.sign):
            score += 5
        elif _sign_distance(mars_a.sign, mars_b.sign) == 6:
            score -= 3

    asc_d = _sign_distance(chart_a.ascendant_sign, chart_b.ascendant_sign)
    if asc_d in (0, 4, 8):
        score += 7
        reasons.append("Ascendants share harmonious sign geometry.")
    elif asc_d == 6:
        score -= 3

    if num_a.mulyank == num_b.mulyank:
        score += 6
        reasons.append("Mulyank values match, giving similar instinctive rhythms.")
    if num_a.bhagyank == num_b.bhagyank:
        score += 5
        reasons.append("Bhagyank values match, giving similar long-term priorities.")

    return max(20, min(92, round(score))), reasons


def generate_relationship_advice(chart_a, chart_b, num_a, num_b, score, retriever, client):
    chunks = retrieve_classical_context(
        retriever,
        "Vedic astrology marriage relationship compatibility seventh house Venus Jupiter Moon Navamsa relationship advice",
    )
    sources = "\n\n".join(
        f"[{c['source_file']} p.{c['page_number']}]\n{c['text']}" for c in chunks
    ) or "No classical passage retrieved."
    prompt = f"""Analyse relationship dynamics between two people using their actual charts.

PERSON A
{_chart_context(chart_a)}
Mulyank={num_a.mulyank}; Bhagyank={num_a.bhagyank}

PERSON B
{_chart_context(chart_b)}
Mulyank={num_b.mulyank}; Bhagyank={num_b.bhagyank}

Compatibility heuristic index: {score}/100

CLASSICAL CONTEXT
{sources}

Return:
1. Relationship dynamic
2. Emotional compatibility
3. Communication style
4. Attraction and conflict patterns
5. Long-term partnership themes
6. Specific dos (5)
7. Specific don'ts (5)
8. Three practical habits for this pair

Do not present the percentage as scientific fact. Do not invent placements or exact future events. Make the advice specific to the two charts."""
    return _call_groq(
        client,
        "You are PrashnaAI's relationship astrology advisor. Use only the supplied chart data and clearly distinguish traditional interpretation from certainty.",
        prompt,
        max_tokens=2200,
    )


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------

def build_chart_from(name, dob, tob, location):
    chart = calculate_birth_chart(
        name=name,
        birth_date=dob.isoformat(),
        birth_time=tob.strftime("%H:%M"),
        utc_offset_hours=location.utc_offset_hours,
        latitude=location.latitude,
        longitude=location.longitude,
        place_name=f"{location.matched_city}, {location.country}",
    )

    st.session_state["chart"] = chart
    st.session_state["numerology"] = calculate_numerology(dob.isoformat())
    st.session_state["location"] = location
    st.session_state["birth_dt_label"] = (
        f"{dob.strftime('%d %B %Y')}, "
        f"{tob.strftime('%I:%M %p').lstrip('0')}"
    )

    # A new chart must never reuse another person's readings.
    for key in list(st.session_state.keys()):
        if key.startswith("narrative_") or key.startswith("monthly_"):
            st.session_state.pop(key, None)
    st.session_state["auto_generate_predictions"] = True


PENDING_KEYS = (
    "pending_place_query",
    "pending_place_candidates",
    "pending_place_labels",
    "pending_name",
    "pending_dob",
    "pending_tob",
)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.html(
        '<div class="pa-side-brand">PrashnaAI</div>'
        '<div class="pa-side-kicker">A quiet space for your chart, numbers and planetary patterns.</div>'
        '<div class="pa-side-section">Birth details</div>'
        '<div class="pa-side-note">Enter accurate birth details. Even a small time difference can change the ascendant.</div>'
    )

    with st.form("birth_details_form"):
        name = st.text_input(
            "Name",
            placeholder="Ananya Arora",
        )

        place = st.text_input(
            "Place of birth",
            placeholder="Gorakhpur, Uttar Pradesh",
        )

        dob = st.date_input(
            "Date of birth",
            value=date(1995, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
        )

        st.caption("Time of birth")

        t1, t2, t3 = st.columns([1, 1, 1.1])

        with t1:
            hour_12 = st.number_input(
                "Hour",
                min_value=1,
                max_value=12,
                value=12,
                step=1,
            )

        with t2:
            minute = st.number_input(
                "Minute",
                min_value=0,
                max_value=59,
                value=0,
                step=1,
            )

        with t3:
            am_pm = st.selectbox(
                "AM/PM",
                ["AM", "PM"],
            )

        submitted = st.form_submit_button(
            "Build my chart",
            **STRETCH,
        )

    if "location" in st.session_state:
        loc = st.session_state["location"]
        st.html(
            f'<div class="pa-side-note" style="margin-top:.7rem;">'
            f'✓ Using {loc.matched_city}, {loc.country}<br>'
            f'<span style="font-size:.62rem;">{loc.latitude:.3f}, {loc.longitude:.3f} · UTC{loc.utc_offset_hours:+.1f}</span>'
            f'</div>'
        )

    if "numerology" in st.session_state:
        n = st.session_state["numerology"]
        st.html(
            '<div class="pa-side-orbit">'
            '<div class="pa-zodiac-line">♈ ♉ ♊ ♋ ♌ ♍</div>'
            '<div class="pa-zodiac-line">♎ ♏ ♐ ♑ ♒ ♓</div>'
            '<div class="pa-side-orbit-note">12 signs · 9 planets · numerology</div>'
            '<div class="pa-side-mini">'
            f'<div class="pa-mini"><div class="pa-mini-label">Mulyank</div><div class="pa-mini-value">{n.mulyank}</div></div>'
            f'<div class="pa-mini"><div class="pa-mini-label">Bhagyank</div><div class="pa-mini-value">{n.bhagyank}</div></div>'
            '</div></div>'
        )


# ---------------------------------------------------------------------------
# Time conversion
# ---------------------------------------------------------------------------

hour_24 = 0 if hour_12 == 12 else int(hour_12)

if am_pm == "PM":
    hour_24 += 12

tob = time(hour_24, int(minute))


# ---------------------------------------------------------------------------
# Submit handling
# ---------------------------------------------------------------------------

if submitted:
    if not name.strip() or not place.strip():
        st.sidebar.error(
            "Enter a name and a place of birth to continue."
        )
    else:
        try:
            location = resolve_place(
                place.strip(),
                birth_date=dob,
            )

        except AmbiguousPlaceError as e:
            st.session_state.update(
                {
                    "pending_place_query": place.strip(),
                    "pending_place_candidates": e.candidates,
                    "pending_place_labels": e.candidate_labels(),
                    "pending_name": name.strip(),
                    "pending_dob": dob,
                    "pending_tob": tob,
                }
            )

            st.session_state.pop("chart", None)

        except PlaceNotFoundError as e:
            st.sidebar.error(str(e))

        else:
            for key in PENDING_KEYS:
                st.session_state.pop(key, None)

            build_chart_from(
                name.strip(),
                dob,
                tob,
                location,
            )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

if "chart" in st.session_state:
    chart = st.session_state["chart"]
    st.html(
        '<div class="pa-topbar">'
        '<div class="pa-brandmark"><span class="pa-orbit"></span>PrashnaAI</div>'
        '<div class="pa-topnote">Sidereal · RAG grounded · AI assisted</div>'
        '</div>'
        '<div class="pa-hero">'
        '<div class="pa-eyebrow">Your personal celestial map</div>'
        '<div class="pa-title">Read the patterns.<br>Understand the chart.</div>'
        f'<div class="pa-subtitle">{chart.name} · {chart.place_name} · {st.session_state["birth_dt_label"]}</div>'
        '<div class="pa-meta-row">'
        '<span class="pa-chip">☉ Birth chart</span>'
        '<span class="pa-chip">☽ Moon & Nakshatra</span>'
        '<span class="pa-chip">✦ Numerology</span>'
        '<span class="pa-chip">↝ Year ahead</span>'
        '</div></div>'
    )
else:
    st.html(
        '<div class="pa-topbar">'
        '<div class="pa-brandmark"><span class="pa-orbit"></span>PrashnaAI</div>'
        '<div class="pa-topnote">Vedic astrology · Numerology</div>'
        '</div>'
        '<div class="pa-hero">'
        '<div class="pa-eyebrow">An intelligent astrology workspace</div>'
        '<div class="pa-title">Your chart,<br>beautifully interpreted.</div>'
        '<div class="pa-subtitle">Build a sidereal birth chart, explore numerology, and generate AI-assisted readings grounded in classical source material.</div>'
        '<div class="pa-meta-row">'
        '<span class="pa-chip">♈ 12 signs</span>'
        '<span class="pa-chip">☉ Planetary positions</span>'
        '<span class="pa-chip">✦ Numerology</span>'
        '<span class="pa-chip">☽ Monthly transits</span>'
        '</div></div>'
    )


# ---------------------------------------------------------------------------
# Place disambiguation
# ---------------------------------------------------------------------------

if "pending_place_candidates" in st.session_state:
    st.markdown(
        f"""
        <div class="pa-section">
            Which {st.session_state["pending_place_query"]}?
        </div>
        <div class="pa-section-note">
            More than one place carries this name. Choose the correct place
            so the chart uses the correct coordinates.
        </div>
        """,
        unsafe_allow_html=True,
    )

    labels = st.session_state["pending_place_labels"]

    idx = st.radio(
        "Matching places",
        options=list(range(len(labels))),
        format_func=lambda i: labels[i],
        label_visibility="collapsed",
    )

    if st.button("Use this place", **STRETCH):
        chosen = st.session_state["pending_place_candidates"][idx]

        location = resolve_from_candidate(
            chosen,
            st.session_state["pending_place_query"],
            st.session_state["pending_dob"],
        )

        build_chart_from(
            st.session_state["pending_name"],
            st.session_state["pending_dob"],
            st.session_state["pending_tob"],
            location,
        )

        for key in PENDING_KEYS:
            st.session_state.pop(key, None)

        st.rerun()


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------

if "chart" not in st.session_state:
    if "pending_place_candidates" not in st.session_state:
        st.html(
            '<div class="pa-empty">'
            '<div class="pa-empty-icon">☽</div>'
            '<div class="pa-empty-title">Begin with your birth details</div>'
            '<div class="pa-empty-text">Enter your details in the left panel to create your celestial map. Your planetary placements, Moon sign, Nakshatra and numerology will become the foundation for the prediction engine.</div>'
            '</div>'
        )

    st.stop()


# ---------------------------------------------------------------------------
# Current chart data
# ---------------------------------------------------------------------------

chart = st.session_state["chart"]
numerology = st.session_state["numerology"]
moon = chart.planets["Moon"]


def fact(
    label: str,
    value: str,
    hindi: str = "",
    numeric: bool = False,
) -> str:
    # Keep every HTML line flush-left. Indented HTML inside st.markdown()
    # can be interpreted as a Markdown code block by Streamlit.
    cls = "pa-fact-value pa-num" if numeric else "pa-fact-value"
    hindi_html = f'<span class="pa-hi">{hindi}</span>' if hindi else ""
    return (
        f'<div class="pa-fact">'
        f'<div class="pa-fact-label">{label}</div>'
        f'<div class="{cls}">{value}</div>'
        f'{hindi_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Visual overview
# ---------------------------------------------------------------------------

st.html(
    '<div class="pa-welcome">'
    '<div class="pa-welcome-card">'
    '<div class="pa-welcome-kicker">Celestial overview</div>'
    f'<div class="pa-welcome-title">{chart.ascendant_sign} rising · {moon.sign} Moon</div>'
    '<div class="pa-welcome-text">Your dashboard combines chart calculation, classical-source retrieval, AI-assisted interpretation and numerology in one place.</div>'
    '</div>'
    '<div class="pa-welcome-card pa-symbol-panel">'
    '<div class="pa-symbol-ring">☉</div>'
    '<div class="pa-symbol-caption">Sun · Moon · Planets · Numbers</div>'
    '</div>'
    '</div>'
)


# ---------------------------------------------------------------------------
# Fact ribbon
# ---------------------------------------------------------------------------

st.html(
    '<div class="pa-ribbon">'
    + fact("Ascendant", chart.ascendant_sign, chart.ascendant_sign_hindi)
    + fact("Moon sign", moon.sign, moon.sign_hindi)
    + fact("Nakshatra", str(moon.nakshatra), f"Pada {moon.pada}")
    + fact("Mulyank", str(numerology.mulyank), numeric=True)
    + fact("Bhagyank", str(numerology.bhagyank), numeric=True)
    + "</div>"
)


# ---------------------------------------------------------------------------
# Main tabs
# ---------------------------------------------------------------------------

tab_charts, tab_predictions, tab_advice, tab_year = st.tabs(
    [
        "Charts & numerology",
        "Predictions",
        "Relationship & Advice",
        "Year ahead",
    ]
)


# ---------------------------------------------------------------------------
# TAB 1 — Charts
# ---------------------------------------------------------------------------

with tab_charts:
    st.markdown(
        '<div class="pa-section">Your chart</div>'
        '<div class="pa-section-note">'
        'Planetary positions calculated from the birth details above. '
        'The tables show the underlying chart data used by the reading system.'
        '</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.55, 1], gap="large")

    with left:
        st.markdown(
            '<div class="pa-section">Rashi chart · D1</div>'
            '<div class="pa-section-note">'
            'Planetary positions at birth, by sign and house.'
            '</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(
            [
                {
                    "Planet": p.name,
                    "Sign": f"{p.sign} ({p.sign_hindi})",
                    "House": p.house,
                    "Nakshatra": f"{p.nakshatra} · {p.pada}",
                    "Retro": "R" if p.retrograde else "",
                }
                for p in chart.planets.values()
            ],
            **STRETCH,
            hide_index=True,
        )

        st.markdown(
            '<div class="pa-section" style="margin-top:1.7rem;">'
            'Navamsa chart · D9'
            '</div>'
            '<div class="pa-section-note">'
            "The divisional chart traditionally read for marriage and a "
            "planet's underlying strength."
            '</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(
            [
                {
                    "Planet": p.name,
                    "Sign": f"{p.sign} ({p.sign_hindi})",
                    "House": p.house,
                }
                for p in chart.navamsa_planets.values()
            ],
            **STRETCH,
            hide_index=True,
        )

    with right:
        st.markdown(
            '<div class="pa-section">Numerology</div>'
            '<div class="pa-section-note">'
            'Derived from the date of birth alone.'
            '</div>',
            unsafe_allow_html=True,
        )

        n1, n2 = st.columns(2)

        with n1:
            st.markdown(
                f"""
                <div class="pa-card">
                    <div class="pa-card-label">Mulyank</div>
                    <div class="pa-card-value">{numerology.mulyank}</div>
                    <div class="pa-card-note">
                        Ruled by {numerology.mulyank_ruler}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with n2:
            st.markdown(
                f"""
                <div class="pa-card">
                    <div class="pa-card-label">Bhagyank</div>
                    <div class="pa-card-value">{numerology.bhagyank}</div>
                    <div class="pa-card-note">
                        Ruled by {numerology.bhagyank_ruler}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="pa-card">
                <div class="pa-card-label">Lucky numbers</div>
                <div class="pa-card-value">
                    {", ".join(str(n) for n in numerology.lucky_numbers)}
                </div>
                <div class="pa-card-note">
                    Lucky colours:
                    {", ".join(numerology.lucky_colors)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="pa-card">
                <div class="pa-card-label">Lucky colours</div>
                <div class="pa-card-value">
                    {", ".join(numerology.lucky_colors)}
                </div>
                <div class="pa-card-note">
                    {", ".join(numerology.lucky_colors_hindi)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# TAB 2 — Predictions
# ---------------------------------------------------------------------------

with tab_predictions:
    st.markdown(
        '<div class="pa-section">Your personalised predictions</div>'
        '<div class="pa-section-note">Every area is generated from this exact birth chart. The engine combines planetary placements with retrieved classical passages and a current Groq model.</div>',
        unsafe_allow_html=True,
    )

    prediction_items = list(TOPIC_LABELS.items())
    pending_auto = st.session_state.get("auto_generate_predictions", False)

    if pending_auto:
        st.session_state["auto_generate_predictions"] = False
        progress = st.progress(0, text="Building your personalised readings…")
        try:
            retriever = load_retriever()
            groq_client = load_groq_client()
            total = len(prediction_items)
            for i, (topic, label) in enumerate(prediction_items, start=1):
                key = f"narrative_{topic}"
                if key not in st.session_state:
                    try:
                        st.session_state[key] = generate_unique_prediction(
                            chart, topic, label, retriever, groq_client
                        )
                    except Exception as exc:
                        st.session_state[f"prediction_error_{topic}"] = str(exc)
                progress.progress(i / total, text=f"Prepared {i} of {total} areas")
        finally:
            progress.empty()

    c1, c2 = st.columns([2.2, 1])
    with c1:
        if st.button("↻ Regenerate all predictions", key="regen_predictions", **STRETCH):
            for key in list(st.session_state.keys()):
                if key.startswith("narrative_") or key.startswith("prediction_error_"):
                    st.session_state.pop(key, None)
            st.session_state["auto_generate_predictions"] = True
            st.rerun()
    with c2:
        st.markdown(
            f'<div class="pa-card"><div class="pa-card-label">AI model</div><div class="pa-card-value" style="font-size:1rem">{escape(GROQ_MODEL)}</div><div class="pa-card-note">Current Groq production model</div></div>',
            unsafe_allow_html=True,
        )

    generated_count = 0
    for topic, label in prediction_items:
        result_key = f"narrative_{topic}"
        error_key = f"prediction_error_{topic}"
        if result_key not in st.session_state and error_key not in st.session_state:
            continue
        generated_count += int(result_key in st.session_state)
        with st.expander(f"✦ {label.title()}", expanded=(generated_count == 1)):
            if error_key in st.session_state:
                st.error(
                    f"This prediction could not be generated: {st.session_state[error_key]}"
                )
                continue
            result = st.session_state[result_key]
            st.markdown(f'<div class="pa-reading">{result["narrative"]}</div>', unsafe_allow_html=True)
            chunks = result.get("retrieved_chunks", [])
            if chunks:
                with st.popover("Classical sources"):
                    for chunk in chunks:
                        st.caption(
                            f'{chunk.get("source_file", "Source")} · page {chunk.get("page_number", "?")} · match {chunk.get("score", "")}'
                        )
                        st.text(chunk["text"][:500])

    if not generated_count and not pending_auto:
        st.info("Build a new chart to generate all life-area predictions automatically.")


# ---------------------------------------------------------------------------
# TAB 3 — Relationship & Advice
# ---------------------------------------------------------------------------

with tab_advice:
    st.markdown(
        '<div class="pa-section">Relationship intelligence</div>'
        '<div class="pa-section-note">Compare two birth charts, explore relationship patterns, and receive practical do/don\'t guidance. The compatibility percentage is a traditional-style heuristic, not a scientifically validated probability.</div>',
        unsafe_allow_html=True,
    )

    advice_tab, compatibility_tab = st.tabs(["My relationship advice", "Match two people"])

    with advice_tab:
        st.markdown(
            '<div class="pa-card"><div class="pa-card-label">Your relationship profile</div>'
            '<div class="pa-card-value">Personalised guidance for how you connect</div>'
            '<div class="pa-card-note">Uses your Moon, Venus, Mars, Ascendant, houses, Navamsa and numerology as available in the calculated chart.</div></div>',
            unsafe_allow_html=True,
        )
        relationship_key = next(
            (f"narrative_{topic}" for topic, label in TOPIC_LABELS.items() if "relationship" in str(label).lower()),
            None,
        )
        if relationship_key and relationship_key in st.session_state:
            result = st.session_state[relationship_key]
            st.markdown('<div class="pa-section">Relationship reading</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="pa-reading">{result["narrative"]}</div>', unsafe_allow_html=True)
        else:
            st.info("Your relationship prediction is generated with the other life areas. If it failed, the Predictions page shows the exact error.")

    with compatibility_tab:
        st.markdown('<div class="pa-section">Compatibility by birth chart</div>', unsafe_allow_html=True)
        st.caption("Enter the second person's exact birth details. The first person is the chart currently loaded in PrashnaAI.")
        with st.form("compatibility_form"):
            b_name = st.text_input("Second person's name", key="compat_name")
            b_place = st.text_input("Second person's place of birth", key="compat_place")
            b_dob = st.date_input(
                "Second person's date of birth",
                value=date(1995, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                key="compat_dob",
                format="DD/MM/YYYY",
            )
            bt1, bt2, bt3 = st.columns([1, 1, 1.1])
            with bt1:
                b_hour = st.number_input("Hour", 1, 12, 12, key="compat_hour")
            with bt2:
                b_min = st.number_input("Minute", 0, 59, 0, key="compat_min")
            with bt3:
                b_ampm = st.selectbox("AM/PM", ["AM", "PM"], key="compat_ampm")
            match_submit = st.form_submit_button("Calculate compatibility", **STRETCH)

        if match_submit:
            if not b_name.strip() or not b_place.strip():
                st.error("Enter the second person's name and place of birth.")
            else:
                b_h24 = b_hour % 12 + (12 if b_ampm == "PM" else 0)
                b_tob = time(int(b_h24), int(b_min))
                try:
                    b_location = resolve_place(b_place.strip(), birth_date=b_dob)
                    chart_b = calculate_birth_chart(
                        name=b_name.strip(),
                        birth_date=b_dob.isoformat(),
                        birth_time=b_tob.strftime("%H:%M"),
                        utc_offset_hours=b_location.utc_offset_hours,
                        latitude=b_location.latitude,
                        longitude=b_location.longitude,
                        place_name=f"{b_location.matched_city}, {b_location.country}",
                    )
                    num_b = calculate_numerology(b_dob.isoformat())
                    score, reasons = compatibility_analysis(chart, chart_b, numerology, num_b)
                    st.session_state["compatibility_result"] = {
                        "chart_b": chart_b,
                        "num_b": num_b,
                        "score": score,
                        "reasons": reasons,
                    }
                    st.session_state.pop("compatibility_ai", None)
                except AmbiguousPlaceError:
                    st.error("The second person's place is ambiguous. Add city + state/country.")
                except PlaceNotFoundError as exc:
                    st.error(str(exc))
                except Exception as exc:
                    st.error(f"Compatibility could not be calculated: {exc}")

        if "compatibility_result" in st.session_state:
            cr = st.session_state["compatibility_result"]
            chart_b = cr["chart_b"]
            num_b = cr["num_b"]
            score = cr["score"]
            left, right = st.columns([1.1, 1.9])
            with left:
                st.markdown(
                    f'<div class="pa-compat-score"><div class="pa-compat-number">{score}%</div><div class="pa-compat-label">Compatibility index</div><div class="pa-card-note">Traditional heuristic from chart and numerology features</div></div>',
                    unsafe_allow_html=True,
                )
            with right:
                st.markdown('<div class="pa-section" style="margin-top:0">What shapes the match</div>', unsafe_allow_html=True)
                for reason in cr["reasons"]:
                    st.markdown(f"- {reason}")

            st.markdown('<div class="pa-section">Dos & don\'ts</div>', unsafe_allow_html=True)
            d1, d2 = st.columns(2)
            with d1:
                st.markdown(
                    '<div class="pa-advice-do"><div class="pa-card-label">DO</div><ul>'
                    '<li>Make communication explicit instead of assuming intent.</li>'
                    '<li>Give each other room for different emotional rhythms.</li>'
                    '<li>Discuss money, boundaries and expectations early.</li>'
                    '<li>Use the strengths shown by both charts rather than comparing them.</li>'
                    '<li>Revisit difficult topics when both people are calm.</li>'
                    '</ul></div>', unsafe_allow_html=True,
                )
            with d2:
                st.markdown(
                    '<div class="pa-advice-dont"><div class="pa-card-label">DON\'T</div><ul>'
                    '<li>Use the percentage as a verdict on the relationship.</li>'
                    '<li>Turn astrological differences into blame.</li>'
                    '<li>Make major life decisions from a prediction alone.</li>'
                    '<li>Assume attraction automatically means compatibility.</li>'
                    '<li>Ignore real-world behaviour, consent or communication.</li>'
                    '</ul></div>', unsafe_allow_html=True,
                )

            if st.button("Generate personalised relationship advice", key="generate_relationship_advice", **STRETCH):
                with st.spinner("Analysing both charts…"):
                    try:
                        advice = generate_relationship_advice(
                            chart, chart_b, numerology, num_b, score,
                            load_retriever(), load_groq_client(),
                        )
                        st.session_state["compatibility_ai"] = advice
                    except Exception as exc:
                        st.error(f"Relationship advice could not be generated: {exc}")

            if "compatibility_ai" in st.session_state:
                st.markdown('<div class="pa-section">Personalised relationship advice</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="pa-reading">{st.session_state["compatibility_ai"]}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# TAB 2 — Year ahead
# ---------------------------------------------------------------------------

with tab_year:
    st.markdown(
        '<div class="pa-section">The next twelve months</div>'
        '<div class="pa-section-note">'
        'Each month is read from planetary transits against the birth chart. '
        'Open a month to generate its reading. Results are cached in the '
        'session so an already-generated month is not regenerated.'
        '</div>',
        unsafe_allow_html=True,
    )

    transits = list(
        calculate_monthly_transits(
            chart,
            months=12,
        )
    )

    for i, transit in enumerate(transits):
        month_key = f"monthly_{transit.period_start.isoformat()}"

        with st.expander(
            transit.month_label,
            expanded=(i == 0),
        ):
            if month_key not in st.session_state:
                if i == 0:
                    with st.spinner(
                        f"Generating {transit.month_label} prediction…"
                    ):
                        try:
                            st.session_state[month_key] = (
                                generate_monthly_narrative_groq(
                                    chart,
                                    transit,
                                    load_retriever(),
                                    client=load_groq_client(),
                                )
                            )
                        except Exception as exc:
                            st.error(
                                f"Couldn't generate this month: {exc}"
                            )
                else:
                    if st.button(
                        f"Generate {transit.month_label} prediction",
                        key=f"generate_month_{i}",
                        **STRETCH,
                    ):
                        with st.spinner(
                            f"Generating {transit.month_label} prediction…"
                        ):
                            try:
                                st.session_state[month_key] = (
                                    generate_monthly_narrative_groq(
                                        chart,
                                        transit,
                                        load_retriever(),
                                        client=load_groq_client(),
                                    )
                                )
                                st.rerun()
                            except Exception as exc:
                                st.error(
                                    f"Couldn't generate this month: {exc}"
                                )

            if month_key in st.session_state:
                result = st.session_state[month_key]

                if result["sade_sati_phase"]:
                    st.markdown(
                        f"""
                        <div class="pa-flag">
                            Sade Sati — {result["sade_sati_phase"]}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                if result["ingresses"]:
                    st.markdown(
                        f"""
                        <div class="pa-ingress">
                            Sign changes:
                            {"; ".join(result["ingresses"])}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f'<div class="pa-reading">{result["narrative"]}</div>',
                    unsafe_allow_html=True,
                )

                with st.popover("Sources"):
                    for chunk in result["retrieved_chunks"]:
                        st.caption(
                            f'{chunk["source_file"]}, '
                            f'page {chunk["page_number"]} · '
                            f'match {chunk["score"]:.2f}'
                        )

                        st.text(
                            chunk["text"][:300]
                            + (
                                "…"
                                if len(chunk["text"]) > 300
                                else ""
                            )
                        )


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="pa-footer">
        PrashnaAI · Sidereal calculations · AI-assisted interpretation
    </div>
    """,
    unsafe_allow_html=True,
)

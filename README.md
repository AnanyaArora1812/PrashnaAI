# 🔮 PrashnaAI

## AI-Powered Personalized Astrology Intelligence Platform

PrashnaAI is a **Generative AI-powered astrology application** that combines **astrological chart calculation, numerology, Retrieval-Augmented Generation (RAG), semantic search, and Large Language Models (LLMs)** to generate personalized astrology insights.

Instead of functioning as a traditional astrology chatbot, PrashnaAI uses an individual's **date of birth, time of birth, and birth place** to calculate relevant astrological information and generate personalized interpretations across different areas of life.

The application combines structured calculations with domain-specific knowledge retrieval and **Groq-based LLM generation** to create a personalized astrology experience.

> **Core Domains:** Generative AI · LLMs · RAG · NLP · Semantic Search · AI Personalization

---

## ✨ Key Features

### 🌌 Personalized Astrology Analysis

PrashnaAI creates an individualized astrology profile using the user's birth information.

The application works with:

- Date of birth
- Time of birth
- Birth place
- Ascendant
- Planetary positions
- Moon sign
- Nakshatra-related information
- Other calculated chart information

The generated interpretation is based on the user's calculated chart rather than a generic zodiac horoscope.

---

### 🔢 Numerology

PrashnaAI also integrates numerology into the personalized analysis.

The system calculates values such as:

- **Mulyank**
- **Bhagyank**

These values can be combined with astrological information to provide additional personalized interpretations.

---

## 🔮 Personalized Predictions

PrashnaAI generates AI-based interpretations across different areas of life.

Supported areas include:

- 💼 Career
- 💰 Finance
- ❤️ Relationships
- 🌱 Personal Growth
- 🧠 Personality and tendencies
- 📅 Year-ahead insights

The predictions are generated using the individual's calculated chart information and relevant astrology knowledge.

The goal is to provide **personalized interpretations instead of a fixed generic horoscope**.

---

# ❤️ Relationship Analysis

PrashnaAI includes a dedicated relationship and compatibility module.

The system supports both:

### Individual Relationship Advice

The application can generate personalized relationship-oriented guidance based on the user's chart.

### Two-Person Compatibility

Users can enter the birth information of two people and compare their charts.

The compatibility workflow can provide:

- Compatibility percentage/index
- Emotional compatibility
- Communication patterns
- Attraction-related themes
- Potential areas of conflict
- Long-term relationship themes
- Personalized relationship advice
- Do's
- Don'ts
- Practical relationship habits

The general workflow is:

**Person A Birth Information → Chart A**

**Person B Birth Information → Chart B**

**Chart A + Chart B → Compatibility Analysis → Personalized Relationship Insights**

> **Note:** The compatibility percentage is an application-generated interpretive index and is not a scientifically validated measurement of relationship success.

---

# 📅 Year-Ahead Analysis

PrashnaAI provides a year-ahead analysis based on the user's calculated birth chart and planetary transit information.

The system generates personalized month-wise interpretations to help users explore important astrological themes throughout the upcoming year.

### How It Works

**Birth Chart → Transit Calculation → Monthly Context → Relevant Knowledge → Groq LLM → Personalized Monthly Insights**

The generated insights are presented month by month, allowing users to explore changing themes throughout the year.

---

# 🧠 AI Architecture

PrashnaAI uses a layered architecture that separates **structured calculations, knowledge retrieval, and generative AI**.

### High-Level Flow

**User Birth Information**

↓

**Astrology & Numerology Calculations**

↓

**Structured User Context**

↓

**Relevant Knowledge Retrieval**

↓

**Groq LLM**

↓

**Personalized Interpretation**

↓

**Predictions / Relationship Advice / Compatibility / Year-Ahead Insights**

This approach allows the application to combine deterministic calculations with domain-specific knowledge and natural-language generation.

---

# 🔍 Retrieval-Augmented Generation (RAG)

A major component of PrashnaAI is its **Retrieval-Augmented Generation (RAG)** pipeline.

The project works with astrology knowledge derived from scanned Sanskrit/Hindi astrology literature.

Because the source material is not always available as machine-readable text, the project requires a document-processing and retrieval pipeline.

### RAG Pipeline

**Scanned Astrology Literature**

↓

**OCR Extraction**

↓

**Text Cleaning**

↓

**Text Chunking**

↓

**Multilingual Embeddings**

↓

**FAISS Vector Index**

↓

**Semantic Retrieval**

↓

**Relevant Astrology Knowledge**

↓

**Groq LLM**

↓

**Personalized Output**

The retrieval layer provides domain-specific context to the language model instead of relying entirely on general model knowledge.

---

# 📚 Astrology Knowledge Base

The original knowledge pipeline was designed around scanned Sanskrit/Hindi astrology literature.

The document-processing workflow includes:

- PDF rendering
- OCR extraction
- Text cleaning
- Text normalization
- Chunking
- Multilingual embeddings
- Vector indexing
- Semantic retrieval

The embedding model used in the retrieval pipeline is:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

FAISS is used for vector similarity search.

---

# 🤖 Generative AI Layer

The current PrashnaAI application uses **Groq for LLM inference**.

The LLM acts as the natural-language generation and interpretation layer.

It receives relevant structured information and retrieved domain knowledge and generates natural-language interpretations.

The generation layer is used for:

- Personalized predictions
- Astrology interpretations
- Relationship analysis
- Relationship advice
- Practical guidance
- Year-ahead narratives

The architecture separates calculations from language generation.

### Generation Flow

**Structured Astrological Information**

+

**Retrieved Astrology Knowledge**

↓

**Groq LLM**

↓

**Personalized Natural-Language Interpretation**

---

# 🧩 Why Combine Calculations + RAG + LLM?

A generic LLM can produce fluent responses, but the goal of PrashnaAI is to combine the strengths of multiple components.

PrashnaAI therefore uses:

### Structured Calculations

Used for generating astrology and numerology information from user inputs.

### RAG

Used for retrieving relevant domain-specific astrology knowledge.

### LLM

Used for transforming the structured information and retrieved context into natural-language interpretations.

The overall approach is:

**Structured Calculation + Domain Knowledge Retrieval + Generative AI**

↓

**Personalized Interpretation**

---

# 🎯 Personalization

Personalization is one of the main design goals of PrashnaAI.

Instead of a simple:

**User → Zodiac Sign → Generic Horoscope**

the application follows a more detailed process:

**User Birth Information**

↓

**Birth Chart Calculation**

↓

**Planetary Positions + Ascendant + Moon + Other Chart Factors**

↓

**Numerology**

↓

**Relevant Knowledge Retrieval**

↓

**Groq LLM**

↓

**Personalized Interpretation**

This allows different users to receive interpretations based on their individual input and calculated chart information.

---

# 💕 Compatibility Analysis

PrashnaAI supports a two-person relationship compatibility workflow.

The system accepts birth information for both individuals and calculates their respective astrological information.

### Compatibility Workflow

**Person A**

↓

**Birth Information**

↓

**Chart A**

+

**Person B**

↓

**Birth Information**

↓

**Chart B**

↓

**Compatibility Analysis**

↓

**Compatibility Index / Percentage**

↓

**Relationship Interpretation**

↓

**Personalized Advice**

The system can provide insights related to:

- Emotional connection
- Communication
- Relationship dynamics
- Attraction-related themes
- Conflict patterns
- Long-term relationship themes
- Practical relationship guidance

---

# 🎨 User Interface

PrashnaAI is implemented as a **Streamlit application**.

The application contains dedicated sections for:

### 📊 Charts & Numerology

View calculated astrology and numerology information.

### 🔮 Predictions

Explore personalized predictions across supported life areas.

### ❤️ Relationship & Advice

Access relationship guidance and compare two people.

### 📅 Year Ahead

Explore month-wise and year-ahead interpretations.

The interface uses a light celestial-inspired visual design with:

- Zodiac symbols
- Astrology-inspired background elements
- Celestial motifs
- Soft gradients
- Personalized information cards
- Dedicated navigation sections

The design focuses on keeping the astrology theme visually recognizable while maintaining a clean application interface.

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| LLM Inference | Groq |
| Generative AI | Large Language Models |
| RAG | Retrieval-Augmented Generation |
| Vector Search | FAISS |
| Embeddings | Sentence Transformers |
| Embedding Model | `paraphrase-multilingual-MiniLM-L12-v2` |
| OCR | EasyOCR |
| PDF Processing | PyMuPDF |
| Knowledge Source | Sanskrit/Hindi Astrology Literature |
| Configuration | YAML / JSON where applicable |

---

# 📁 Project Structure

```text
PrashnaAI/
│
├── src/
│   │
│   ├── app.py
│   │
│   ├── astro/
│   │   ├── chart_calculator.py
│   │   ├── geocoding.py
│   │   ├── numerology.py
│   │   ├── narrative.py
│   │   ├── narrative_groq.py
│   │   ├── transit_calculator.py
│   │   └── monthly_narrative.py
│   │
│   └── rag/
│       └── retriever.py
│
├── datasets/
│   └── processed/
│       └── faiss_index/
│           ├── index.faiss
│           └── metadata.json
│
├── models/
│
├── notebooks/
│
├── configs/
│
├── experiments/
│
├── reports/
│
├── tests/
│
└── README.md

# ⚙️ Installation

## 1. Clone the Repository

`git clone https://github.com/AnanyaArora1812/PrashnaAI.git`

`cd PrashnaAI`

## 2. Create a Virtual Environment

### Windows

`python -m venv .venv`

Activate the environment:

`.\.venv\Scripts\Activate.ps1`

## 3. Install Dependencies

`pip install -r requirements.txt`

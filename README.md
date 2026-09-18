# 🔮 PrashnaAI

## AI-Powered Personalized Astrology Intelligence Platform

PrashnaAI is a **Generative AI and Retrieval-Augmented Generation (RAG) based personalized astrology intelligence platform** that combines astrological calculations, numerology, domain-specific knowledge retrieval, semantic search, multilingual embeddings, and Large Language Models.

The application combines **structured astrology calculations + numerology + RAG + semantic search + FAISS + Groq LLM inference** to generate personalized, context-aware astrology interpretations.

> **Core Technologies:** Generative AI · LLMs · RAG · NLP · Semantic Search · Vector Search · Multilingual Embeddings · AI Personalization


---

# 🌟 Project Overview

PrashnaAI is designed as a domain-specific AI application that combines traditional astrology knowledge with modern Artificial Intelligence techniques.

Instead of relying only on generic horoscope text, the application follows a multi-stage pipeline:

```text
User Birth Details
        ↓
Astrology Calculations
        ↓
Numerology
        ↓
Personalized Chart Context
        ↓
RAG Knowledge Retrieval
        ↓
Relevant Astrology Knowledge
        ↓
Groq LLM
        ↓
Personalized AI Interpretation
```

The core idea is:

> **Calculations provide structured information → RAG provides relevant domain knowledge → LLM generates the personalized interpretation.**

This architecture demonstrates how **Retrieval-Augmented Generation can be applied to a specialized knowledge domain**.


---

# ✨ Key Features

## 🌌 Personalized Astrology Analysis

The application accepts:

- Date of birth
- Time of birth
- Place of birth

The information is used to calculate relevant astrological details and construct a personalized context.

The generated analysis can use:

- Ascendant
- Zodiac signs
- Planetary positions
- Houses
- Birth-chart information
- Numerological values
- Retrieved astrology knowledge


## 🔢 Numerology

PrashnaAI includes numerology-based analysis.

The application calculates:

- **Mulyank**
- **Bhagyank**

These values can be incorporated into the personalized interpretation along with astrological chart information.


## 🔮 Personalized Predictions

PrashnaAI generates topic-specific personalized interpretations across multiple life areas.

Prediction areas include:

- 💼 Career
- 💰 Finance
- 🎓 Education
- ❤️ Relationships
- 👨‍👩‍👧 Family
- 🌱 Personal Growth
- ✈️ Travel
- 🧑‍🤝‍🧑 Social Life
- 🧘 Wellness
- 🌟 Overall Life Themes

The prediction pipeline combines the user's chart context with relevant retrieved knowledge before generating the response.


## ❤️ Relationship Analysis

PrashnaAI provides relationship-oriented analysis.

The application can generate guidance related to:

- Communication
- Emotional patterns
- Relationship expectations
- Attraction
- Conflict patterns
- Personal boundaries
- Relationship growth
- Practical relationship habits


## 👫 Two-Person Compatibility

The application supports compatibility analysis using the birth information of two individuals.

The system can use available information such as:

- Ascendant
- Moon sign
- Venus
- Mars
- Planetary information
- Numerological values
- Other calculated chart information

The output can include:

- Compatibility analysis
- Relationship interpretation
- Compatibility index
- Do's
- Don'ts
- Practical relationship guidance


## 📊 Compatibility Index

PrashnaAI can generate an application-specific compatibility percentage/index.

The compatibility percentage is an **interpretive application feature and is not a scientifically validated measurement**.

The percentage is accompanied by contextual explanation rather than being presented as an objective prediction of relationship success.


## 📅 Year-Ahead Analysis

PrashnaAI provides month-wise year-ahead analysis using:

- Birth chart information
- Transit calculations
- Monthly context
- Retrieved knowledge
- Groq-generated narratives

The system can generate personalized monthly themes and interpretations.


---

# 🧠 Core AI Architecture

PrashnaAI combines deterministic calculations, knowledge retrieval, and Generative AI.

```text
                         USER
                           │
                           ▼
                  Birth Information
                           │
                           ▼
                Astrology Calculations
                           │
                           ▼
                 Numerology Calculation
                           │
                           ▼
                  Personalized Context
                           │
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
     Astrology Knowledge         User Chart Context
              │                         │
              ▼                         │
             OCR                        │
              ↓                         │
       Text Extraction                  │
              ↓                         │
       Text Cleaning                    │
              ↓                         │
          Chunking                      │
              ↓                         │
   Multilingual Embeddings              │
              ↓                         │
       FAISS Vector Index               │
              ↓                         │
      Semantic Retrieval                │
              ↓                         │
      Relevant Knowledge                │
              │                         │
              └────────────┬────────────┘
                           ▼
                    Context Assembly
                           │
                           ▼
                       Groq LLM
                           │
                           ▼
              Personalized AI Response
```


---

# 🔍 Retrieval-Augmented Generation (RAG)

**RAG is one of the core technologies of PrashnaAI.**

The application does not depend only on the language model's internal knowledge.

Instead, PrashnaAI retrieves relevant information from a project-specific astrology knowledge base and provides that retrieved context to the LLM.

### RAG Pipeline

```text
Astrology Literature
        ↓
PDF / Scanned Documents
        ↓
OCR
        ↓
Text Extraction
        ↓
Text Cleaning
        ↓
Text Chunking
        ↓
Multilingual Embeddings
        ↓
FAISS Vector Index
        ↓
Semantic Search
        ↓
Relevant Knowledge Chunks
        ↓
Combine with User Chart Context
        ↓
Groq LLM
        ↓
Personalized Interpretation
```

### Why RAG?

RAG allows PrashnaAI to:

- Use a domain-specific knowledge base
- Retrieve relevant astrology information
- Ground LLM generation in retrieved context
- Process scanned astrology literature
- Support multilingual source material
- Connect domain knowledge with individual chart information
- Reduce dependence on generic LLM knowledge


---

# 📚 Astrology Knowledge Base

PrashnaAI is designed around a domain-specific astrology knowledge base.

The project supports astrology material including **Sanskrit and Hindi literature**.

The knowledge pipeline includes:

1. Source document collection
2. PDF processing
3. OCR
4. Text extraction
5. Text cleaning
6. Text normalization
7. Text chunking
8. Embedding generation
9. FAISS indexing
10. Semantic retrieval

The goal is to transform unstructured astrology literature into searchable knowledge that can be retrieved during AI generation.


---

# 📄 OCR Pipeline

Traditional astrology resources can be available as scanned documents instead of machine-readable text.

PrashnaAI therefore uses an OCR-oriented processing pipeline.

```text
Scanned PDF
     ↓
PDF Page Rendering
     ↓
OCR
     ↓
Extracted Text
     ↓
Text Cleaning
     ↓
Text Chunking
```

The processed text can then be converted into vector representations for semantic retrieval.


---

# 🔤 Multilingual Embeddings

PrashnaAI uses multilingual sentence embeddings for semantic search.

### Embedding Model

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

The embedding model converts text into vector representations that can be compared using semantic similarity.

This is particularly useful for retrieving relevant information from multilingual astrology material.


---

# 🗄️ FAISS Vector Search

PrashnaAI currently uses **FAISS** for vector similarity search.

The processed vector index is stored in:

```text
datasets/processed/faiss_index/
```

Important files include:

```text
index.faiss
metadata.json
```

### Retrieval Workflow

```text
User Query / Chart Context
          ↓
Embedding Generation
          ↓
Vector Similarity Search
          ↓
FAISS
          ↓
Relevant Knowledge Chunks
          ↓
Context for LLM
```


---

# 🤖 Generative AI Layer

PrashnaAI currently uses **Groq** for Large Language Model inference.

The project does **not** use LLaMA as a locally hosted model.

The LLM receives contextual information such as:

- User chart information
- Numerology information
- Selected analysis topic
- Retrieved astrology knowledge

The LLM then generates a natural-language interpretation.

### Generation Pipeline

```text
User Chart Context
        +
Numerology
        +
Retrieved Astrology Knowledge
        ↓
     Groq LLM
        ↓
Personalized AI Interpretation
```

### Current Model

The current default model is configured as:

```text
openai/gpt-oss-120b
```

The model can be configured using:

```text
GROQ_MODEL
```

This allows the LLM model to be changed without modifying the core application logic.


---

# 🎯 Personalization

Personalization is a central component of PrashnaAI.

The system builds a context from individual user information.

This context can contain:

- Birth date
- Birth time
- Birth location
- Ascendant
- Planetary positions
- Zodiac signs
- Houses
- Numerological values
- Selected topic
- Retrieved astrology knowledge

The generated output is therefore based on the available user-specific context instead of relying on a single fixed response.


---

# 🔮 Prediction Architecture

The prediction system follows:

```text
User Birth Information
        ↓
Birth Chart Calculation
        ↓
Structured Chart Context
        ↓
Prediction Topic
        ↓
RAG Retrieval
        ↓
Relevant Knowledge
        ↓
Groq LLM
        ↓
Personalized Prediction
```

Different prediction areas can use topic-specific context and generation instructions.


---

# ❤️ Relationship Intelligence

The relationship system contains two major components:

```text
Individual Relationship Analysis
                +
Two-Person Compatibility Analysis
```

### Individual Relationship Analysis

The system can provide interpretation related to:

- Communication
- Emotional patterns
- Relationship expectations
- Attraction
- Conflict
- Boundaries
- Personal growth
- Relationship habits


### Two-Person Compatibility Analysis

```text
Person A Birth Details
        ↓
Person A Chart
        │
        ├──────────────┐
        │              │
        ▼              ▼
   Chart Factors   Numerology
        │              │
        └──────┬───────┘
               │
               ▼
       Compatibility Context
               ▲
               │
        ┌──────┴───────┐
        │              │
Person B Chart    Person B Numerology
        ▲              ▲
        │              │
Person B Birth Details
```

The system can compare available astrological and numerological information to generate an interpretive relationship analysis.


---

# 📊 Compatibility Output

The compatibility module can produce:

### Compatibility Index

An application-generated percentage/index.

### Relationship Interpretation

A natural-language explanation based on the available chart and numerological context.

### Do's

Practical relationship-oriented suggestions.

### Don'ts

Potential behaviors or communication patterns to approach carefully.

### Practical Advice

Actionable suggestions generated from the combined context.


---

# 📅 Year-Ahead Analysis

The year-ahead module uses transit information and personalized chart context.

```text
Birth Chart
     ↓
Transit Calculation
     ↓
Monthly Context
     ↓
Relevant Knowledge Retrieval
     ↓
Groq LLM
     ↓
Monthly Narrative
```

The analysis can provide month-wise interpretations across different areas of life.


---

# 🧮 Astrology Calculation Layer

The astrology calculation layer is kept separate from the LLM generation layer.

Its purpose is to generate structured information that can be passed to the AI pipeline.

```text
Astrology Calculations
        ↓
Structured Data
        ↓
Context Construction
        ↓
RAG Retrieval
        ↓
LLM Generation
```

This separation allows calculation logic and natural-language generation logic to remain modular.


---

# 📍 Place Resolution

PrashnaAI includes place-resolution functionality.

The application resolves user-provided places into geographic information required for the chart calculation pipeline.

Relevant module:

```text
src/astro/geocoding.py
```

Important functions and error handling include:

```text
resolve_place
resolve_from_candidate
PlaceNotFoundError
AmbiguousPlaceError
```

This allows the application to handle invalid or ambiguous place input.


---

# 🖥️ User Interface

PrashnaAI uses **Streamlit** for its web interface.

The UI follows a light celestial visual direction.

The interface includes:

- Light theme
- Astrology-inspired background
- Zodiac symbols
- Celestial elements
- Birth information input
- Astrology chart information
- Numerology
- Personalized predictions
- Relationship analysis
- Two-person compatibility
- Compatibility index
- Relationship advice
- Year-ahead analysis

The interface is designed to combine an astrology-inspired identity with a clean and readable application experience.


---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Streamlit | Web application interface |
| Groq | LLM inference |
| Large Language Models | Natural-language generation |
| Retrieval-Augmented Generation | Domain knowledge grounding |
| Sentence Transformers | Text embeddings |
| `paraphrase-multilingual-MiniLM-L12-v2` | Multilingual semantic embeddings |
| FAISS | Vector similarity search |
| EasyOCR | OCR processing |
| PyMuPDF | PDF processing and page rendering |
| NLP | Text processing and semantic retrieval |
| Astrology Calculation Modules | Structured chart generation |
| YAML / JSON | Configuration and structured data |


---

# 🧠 AI / ML Concepts Demonstrated

PrashnaAI demonstrates practical implementation of:

- Generative AI
- Large Language Models
- Retrieval-Augmented Generation
- Natural Language Processing
- Semantic Search
- Vector Search
- Text Embeddings
- Multilingual NLP
- OCR
- Knowledge Grounding
- Prompt Engineering
- AI Personalization
- Domain-Specific AI
- Context-Aware Generation


---

# 🧩 Application Modules

## Astrology Modules

Main astrology modules are located in:

```text
src/astro/
```

Important modules include:

```text
chart_calculator.py
geocoding.py
narrative.py
narrative_groq.py
numerology.py
transit_calculator.py
monthly_narrative.py
```

### Module Responsibilities

**`chart_calculator.py`**

Handles structured birth-chart calculations.

**`geocoding.py`**

Handles place resolution.

**`numerology.py`**

Calculates numerological values.

**`transit_calculator.py`**

Calculates transit-related information used for monthly analysis.

**`narrative.py`**

Contains narrative-related configuration and topic information.

**`narrative_groq.py`**

Handles Groq-powered topic narrative generation.

**`monthly_narrative.py`**

Handles monthly/year-ahead narrative generation.


## RAG Module

The RAG implementation is located in:

```text
src/rag/
```

Important module:

```text
retriever.py
```

The retriever provides access to the semantic search layer and retrieves relevant knowledge from the processed FAISS index.


---

# 📁 Project Structure

```text
PrashnaAI/
│
├── configs/
│
├── datasets/
│   ├── raw/
│   └── processed/
│       └── faiss_index/
│           ├── index.faiss
│           └── metadata.json
│
├── experiments/
│
├── notebooks/
│
├── reports/
│
├── src/
│   ├── astro/
│   │   ├── chart_calculator.py
│   │   ├── geocoding.py
│   │   ├── monthly_narrative.py
│   │   ├── narrative.py
│   │   ├── narrative_groq.py
│   │   ├── numerology.py
│   │   └── transit_calculator.py
│   │
│   ├── rag/
│   │   └── retriever.py
│   │
│   └── app.py
│
├── tests/
│
├── .gitignore
├── requirements.txt
└── README.md
```

> The repository structure may evolve as the project continues to develop.


---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/AnanyaArora1812/PrashnaAI.git
cd PrashnaAI
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

## 3. Activate the Virtual Environment

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
.venv\Scripts\activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```


---

# 🔑 Environment Configuration

PrashnaAI requires a Groq API key for LLM inference.

### Windows PowerShell

```powershell
$env:GROQ_API_KEY="gsk_your_api_key_here"
```

Optional model configuration:

```powershell
$env:GROQ_MODEL="openai/gpt-oss-120b"
```

### Environment Variables

| Variable | Purpose | Required |
|---|---|---|
| `GROQ_API_KEY` | Authentication for Groq | Yes |
| `GROQ_MODEL` | LLM model selection | No |

### Security

Never place your actual API key directly inside the source code.

Never commit your API key to GitHub.

If a `.env` file is used locally, make sure it is excluded from version control.


---

# 🚀 Running the Application

After activating the virtual environment:

```powershell
streamlit run src/app.py
```

The application will normally be available at:

```text
http://localhost:8501
```


---

# 🔄 Complete Application Workflow

```text
                         USER
                           │
                           ▼
                  Enter Birth Details
                           │
                           ▼
                    Place Resolution
                           │
                           ▼
                 Birth Chart Calculation
                           │
                           ▼
                  Numerology Calculation
                           │
                           ▼
                Build Personalized Context
                           │
                           ▼
                   Select Analysis Area
                           │
                           ▼
                  RAG Semantic Retrieval
                           │
                           ▼
                  Relevant Knowledge
                           │
                           ▼
             Chart Context + RAG Context
                           │
                           ▼
                       Groq LLM
                           │
                           ▼
                Personalized AI Output
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Predictions   Relationship   Year-Ahead
                         Analysis
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    Streamlit UI
```


---

# 🔬 RAG Workflow in Detail

```text
1. Astrology Source Literature
             ↓
2. Scanned PDF / Document
             ↓
3. PDF Page Rendering
             ↓
4. OCR
             ↓
5. Extracted Text
             ↓
6. Text Cleaning
             ↓
7. Text Chunking
             ↓
8. Multilingual Embeddings
             ↓
9. FAISS Index Creation
             ↓
10. User Query / Context
             ↓
11. Semantic Retrieval
             ↓
12. Relevant Knowledge Chunks
             ↓
13. Context Assembly
             ↓
14. Groq LLM
             ↓
15. Generated Personalized Response
```

This separates:

```text
Knowledge Ingestion
        ↓
Knowledge Retrieval
        ↓
Response Generation
```


---

# 🔗 RAG + LLM Interaction

The central AI flow of PrashnaAI is:

```text
                    User
                     ↓
              Birth Information
                     ↓
             Chart Calculation
                     ↓
            Personalized Context
                     │
                     │
                     ▼
              Semantic Retrieval
                     │
                     ▼
             Relevant RAG Chunks
                     │
                     │
                     └──────────────┐
                                    │
                                    ▼
                             Context Assembly
                                    ▲
                                    │
                             Chart Information
                                    │
                                    ▼
                                Groq LLM
                                    │
                                    ▼
                         Personalized Response
```

This architecture allows the LLM to use both **structured user-specific information** and **retrieved domain-specific knowledge**.


---

# 🧪 Evaluation

PrashnaAI can be evaluated across several dimensions.

## Retrieval Quality

Evaluate whether the RAG system retrieves knowledge relevant to the user's query and selected topic.

## Context Relevance

Check whether retrieved information is relevant to the analysis being requested.

## Personalization

Check whether generated responses reflect the individual's available chart information.

## Grounding

Evaluate whether the generated response appropriately uses the retrieved domain knowledge.

## Relevance

Check whether the response directly addresses the requested topic.

## Consistency

Check whether the generated explanation remains consistent with the structured information supplied to the model.

## Generation Quality

Evaluation dimensions can include:

- Relevance
- Coherence
- Clarity
- Context utilization
- Grounding
- Personalization
- Practical usefulness

### Future Evaluation Metrics

A future evaluation framework may include:

- Retrieval Precision
- Retrieval Recall
- Context Relevance
- Faithfulness
- Response Consistency
- Human Evaluation


---

# 🔐 Security

PrashnaAI should follow standard application security practices.

- Store API keys in environment variables.
- Never commit secrets to GitHub.
- Keep secret files out of version control.
- Do not expose API keys in frontend code.
- Validate user inputs.
- Handle external API failures safely.
- Avoid storing unnecessary personal information.
- Handle user-provided information responsibly.


---

# 📊 Current Development Status

The current application includes:

- Birth information input
- Place resolution
- Astrology chart calculation
- Numerology
- RAG-based knowledge retrieval
- Multilingual embeddings
- FAISS vector search
- Groq LLM integration
- Personalized predictions
- Multiple prediction categories
- Relationship analysis
- Two-person compatibility
- Compatibility index
- Relationship Do's and Don'ts
- Practical relationship advice
- Transit-based year-ahead analysis
- Monthly narratives
- Streamlit interface


---

# 🚧 Future Scope

Potential future improvements include:

- Larger astrology knowledge base
- Improved OCR preprocessing
- Better document cleaning
- Improved chunking strategies
- Hybrid keyword + semantic retrieval
- Improved retrieval ranking
- RAG evaluation framework
- More detailed astrology calculations
- Advanced transit analysis
- Improved compatibility methodology
- Saved user reports
- PDF report generation
- User accounts
- Multi-language response generation
- Cloud deployment
- Monitoring and analytics
- Automated evaluation
- Response validation


---

# 🤖 Future Agentic AI Architecture

Agentic AI is a **future extension** of PrashnaAI and is not represented as the current core implementation.

A future version could use specialized agents for different tasks.

```text
                       User Query
                           ↓
                   Orchestrator Agent
                           ↓
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
     Chart Agent       RAG Agent     Numerology Agent
          ↓                ↓                ↓
          └────────────────┼────────────────┘
                           ↓
                 Interpretation Agent
                           ↓
                  Validation Agent
                           ↓
                    Final Response
```

Potential future agents include:

- Chart Analysis Agent
- RAG Retrieval Agent
- Numerology Agent
- Transit Analysis Agent
- Relationship Agent
- Report Generation Agent
- Response Validation Agent


---

# 🗺️ Development Roadmap

## Phase 1 — Foundation

- Astrology calculations
- Numerology
- Place resolution
- Streamlit interface

## Phase 2 — Knowledge & RAG

- Astrology literature collection
- OCR
- Text extraction
- Text cleaning
- Text chunking
- Multilingual embeddings
- FAISS indexing
- Semantic retrieval

## Phase 3 — Generative AI

- Groq integration
- Prompt engineering
- Context construction
- RAG-grounded generation
- Personalized generation

## Phase 4 — Personalized Intelligence

- Multiple prediction categories
- Relationship analysis
- Two-person compatibility
- Compatibility index
- Relationship advice
- Do's and Don'ts

## Phase 5 — Advanced Analysis

- Year-ahead analysis
- Monthly narratives
- Transit analysis
- Improved retrieval
- Evaluation framework

## Phase 6 — Future AI Evolution

- Agentic AI
- Specialized AI agents
- Automated validation
- Advanced personalization
- Long-term conversational intelligence


---

# ⚠️ Responsible Use

PrashnaAI is an experimental AI-based astrology interpretation system.

The generated results are intended for **informational and entertainment purposes**.

Astrology interpretations and AI-generated predictions are not scientifically validated predictions.

The application should not be used as the sole basis for important:

- Medical decisions
- Financial decisions
- Legal decisions
- Educational decisions
- Relationship decisions
- Other high-impact decisions

AI-generated content may contain errors, uncertainty, or incomplete interpretations.


---

# 🎓 Academic & Technical Value

PrashnaAI demonstrates how multiple AI technologies can be combined into a domain-specific intelligent application.

The project brings together:

```text
Domain Knowledge
       +
OCR
       +
NLP
       +
Text Embeddings
       +
Vector Search
       +
RAG
       +
LLM
       +
Personalization
       ↓
Domain-Specific Generative AI Application
```

The project demonstrates practical work in:

- Data processing
- Knowledge engineering
- NLP
- Semantic search
- RAG
- LLM integration
- AI personalization
- Application development


---

# 🎯 Project Domains

PrashnaAI demonstrates practical implementation across:

- Artificial Intelligence
- Generative AI
- Machine Learning
- Large Language Models
- Retrieval-Augmented Generation
- Natural Language Processing
- Semantic Search
- Vector Databases
- Multilingual AI
- OCR
- Text Embeddings
- Prompt Engineering
- Knowledge Grounding
- AI Personalization
- Software Engineering


---

# 💼 Resume Description

### PrashnaAI — Generative AI & RAG-Based Personalized Astrology Intelligence Platform

Developed a domain-specific Generative AI application integrating **astrological chart calculations, numerology, Retrieval-Augmented Generation (RAG), OCR, multilingual embeddings, FAISS semantic search, and Groq-powered Large Language Models** to generate personalized astrology interpretations, predictions, relationship analysis, compatibility insights, and year-ahead narratives.

Built a knowledge retrieval pipeline that processes scanned astrology literature through **OCR, text preprocessing, chunking, multilingual sentence embeddings, and FAISS indexing**, then combines retrieved knowledge with user-specific chart context before LLM generation.


---

# 🧾 Technical Summary

## Artificial Intelligence

- Generative AI
- Large Language Models
- Retrieval-Augmented Generation
- Prompt Engineering
- AI Personalization

## Machine Learning & NLP

- Semantic Search
- Text Embeddings
- Multilingual NLP
- Vector Similarity Search
- Natural Language Processing

## Knowledge Engineering

- OCR
- PDF Processing
- Text Cleaning
- Text Chunking
- Knowledge Base Construction
- FAISS Indexing

## Application Engineering

- Python
- Streamlit
- Modular Architecture
- API Integration
- Environment Configuration


---

# 🔬 Project Architecture Summary

```text
                       PRASHNAAI
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
 Astrology            Numerology             RAG
 Calculations         Calculations          Pipeline
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                 Personalized Context
                           │
                           ▼
                  Semantic Retrieval
                           │
                           ▼
                 Relevant Knowledge
                           │
                           ▼
                       Groq LLM
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Predictions   Relationships   Year-Ahead
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                 Personalized AI Output
```


---

# 🌱 Why This Project?

PrashnaAI explores the practical application of **RAG and Generative AI in a specialized knowledge domain**.

The project demonstrates that an LLM application can be designed as a complete AI pipeline rather than simply sending a prompt to an API.

The architecture combines:

```text
Structured Computation
        +
Domain-Specific Knowledge
        +
Semantic Retrieval
        +
Generative AI
        +
Personalization
```

The project therefore demonstrates an end-to-end AI system involving:

- Data processing
- Knowledge ingestion
- OCR
- Embeddings
- Vector search
- RAG
- LLM integration
- Prompt engineering
- Personalized generation
- User-facing AI application development


---

# 🔒 Important Technology Note

PrashnaAI currently uses:

```text
Groq
```

for LLM inference.

The current architecture does **not** depend on:
The Generative AI layer is designed around the Groq API and configurable Groq model selection.


---

# 📌 Key Project Keywords

```text
Generative AI
RAG
Retrieval-Augmented Generation
LLM
Groq
NLP
Semantic Search
Vector Search
FAISS
Embeddings
Multilingual Embeddings
OCR
Knowledge Base
AI Personalization
Prompt Engineering
Streamlit
Python
Astrology AI
Numerology
Relationship Analysis
Compatibility Analysis
```

---

# 👩‍💻 Author

## Ananya Arora

**B.Tech — Computer Science & Data Science**

GitHub:

https://github.com/AnanyaArora1812


---

# ⭐ PrashnaAI

**Calculations. Knowledge. Retrieval. Generative AI. Personalization.**

# AI-Resume-Intelligence-Agent

## Overview

AI-Resume-Intelligence-Agent is an internship-level GenAI project focused on building an intelligent resume screening and candidate ranking system.

The project combines:

- Deterministic rule-based parsing
- Semantic NLP validation
- Explainable AI preprocessing
- Resume intelligence engineering
- Retrieval-ready chunking architecture

The long-term goal is to evolve this system into an:

# HR Resume & LinkedIn Shortlisting Agent

capable of:
- screening resumes
- understanding candidate profiles
- semantic retrieval
- explainable ranking
- recruiter-facing AI reasoning

---

# Tech Stack

## Core Stack

- Python
- Streamlit
- PyMuPDF
- Sentence Transformers
- FAISS
- Pydantic
- NumPy
- Pandas
- PyTorch
- Transformers

---

# Current Project Structure

```plaintext
AI-Resume-Intelligence-Agent/
│
├── app/
│   ├── ui.py
│   └── components/
│
├── core/
│   ├── parser.py
│   ├── chunker.py
│   ├── parser_utils.py
│   ├── section_aliases.py
│   ├── semantic_boundary.py
│   ├── metadata_extractor.py
│   ├── nlp_section_classifier.py
│   └── security.py
│
├── data/
│   ├── resumes/
│   ├── jd/
│   └── outputs/
│
├── tests/
│
├── requirements.txt
├── README.md
└── main.py
```

---

# Project Goal

Build an AI-powered resume intelligence system that can:

- accept multiple resumes
- accept a Job Description (JD)
- parse and structure resume data
- perform semantic understanding
- generate retrieval-ready chunks
- support vector search
- enable explainable candidate ranking

---

# PHASE 1 — Resume & JD Parsing ✅

## Features Implemented

### Streamlit Upload System
- Multiple PDF upload support
- JD input support
- Analyze trigger

### Resume Parsing
- PDF parsing using PyMuPDF
- Multi-resume handling
- Structured resume objects

### Validation UI
- Resume preview
- JD preview
- Extraction validation

---

# PHASE 2 — Hybrid Semantic Chunking Engine ✅

This phase evolved far beyond basic chunking.

The preprocessing system became a:

# Hybrid Resume Intelligence Pipeline

---

# Phase 2A — Text Cleaning

Implemented:
- whitespace normalization
- line break cleanup
- PDF formatting cleanup
- text normalization

Purpose:
Improve embedding quality and reduce noisy retrieval.

---

# Phase 2B — Rule-Based Resume Section Extraction

Implemented:
- heading detection
- canonical section mapping
- alias normalization
- fallback handling

Supported canonical sections:

- contact_info
- professional_summary
- skills
- projects
- experience
- education
- certifications
- achievements
- research
- leadership
- other

---

# Phase 2C — Advanced Alias System

Created:
`core/section_aliases.py`

Features:
- realistic resume aliases
- heading normalization
- decorated heading detection
- exact heading matching
- regex heuristics

Examples supported:

```plaintext
TECH STACK
TECHNICAL SKILLS
CORE COMPETENCIES
PROJECT EXPERIENCE
CAREER SUMMARY
AWARDS & HONORS
```

---

# Phase 2D — Semantic Boundary Repair

Created:
`core/semantic_boundary.py`

Purpose:
Prevent semantic section bleed.

Example problem:

```plaintext
PROJECTS
Built AI chatbot...

TECH STACK
Python, FastAPI, PyTorch

Worked with APIs...
```

Without semantic repair:
- narrative text could incorrectly remain in skills

Implemented:
- semantic section hints
- narrative flow tracking
- section repair heuristics
- low-signal section merging

---

# Phase 2E — Fallback Routing

Implemented:
- "other" section handling
- malformed section preservation
- unknown heading routing

Purpose:
Avoid losing valuable resume information.

---

# Phase 2F — Metadata Extraction

Created:
`core/metadata_extractor.py`

Extracted:
- candidate name
- email
- phone
- LinkedIn
- GitHub
- portfolio
- location

Used:
- regex extraction
- conservative heuristics
- contact-zone parsing

---

# Phase 2G — Structured Chunk Storage

Implemented:
- section-wise chunking
- chunk overlap support
- structured storage

Chunking goals:
- retrieval quality
- semantic isolation
- embedding preparation

---

# Phase 2H — Hybrid NLP Semantic Validation Layer

Created:
`core/nlp_section_classifier.py`

This became one of the most important architectural decisions.

The system uses:

## Deterministic Rule Parsing FIRST

Then:
## NLP validation ONLY when necessary

---

# Final Hybrid Architecture

```plaintext
Rule-Based Parsing
↓
Regex Heading Detection
↓
Fallback Routing
↓
Semantic Boundary Repair
↓
Parsing Quality Evaluation
↓
Conditional NLP Validation
↓
Disagreement Detection
↓
Fallback Semantic Repair
↓
Section-wise Chunking
```

---

# Why This Architecture Was Chosen

Pure rule systems:
- brittle on edge cases

Pure NLP systems:
- unstable
- expensive
- harder to debug

Hybrid approach provides:
- explainability
- determinism
- semantic awareness
- scalability

---

# NLP Validation Features

Implemented:
- semantic prototype matching
- cosine similarity validation
- disagreement detection
- conservative repair
- confidence scoring
- parsing quality evaluation
- conditional NLP activation

Important:
NLP does NOT replace rule-based parsing.

It only:
- validates
- repairs ambiguous cases
- classifies fallback content

---

# Conditional NLP Activation

NLP activates ONLY when:
- parsing quality is weak
- malformed sections exist
- fallback content is high
- semantic disagreement occurs

Clean resumes skip NLP entirely.

This improves:
- speed
- explainability
- stability

---

# Major Problems Faced & Solutions

## Problem 1 — LangChain Dependency Instability

### Issue
LangChain ecosystem caused:
- dependency conflicts
- import failures
- transformer mismatches
- unstable text splitter behavior

### Solution
Removed:
- langchain
- langgraph
- langchain-community
- langchain-classic

Built:
- fully custom preprocessing pipeline

Result:
- cleaner architecture
- better stability
- lower dependency complexity

---

## Problem 2 — Weak Basic Chunking

### Issue
Naive chunking could:
- split projects incorrectly
- mix sections
- damage retrieval quality

### Solution
Built:
- section-aware chunking
- semantic boundary repair
- hybrid validation pipeline

Result:
- retrieval-ready chunks
- semantic integrity preservation

---

## Problem 3 — Resume Formatting Variability

### Issue
Resumes use:
- inconsistent headings
- missing headings
- decorative formatting
- compressed layouts

### Solution
Implemented:
- alias system
- regex heading heuristics
- fallback routing
- semantic repair

---

## Problem 4 — NLP Overcorrection Risk

### Issue
NLP classifiers can:
- aggressively override sections
- destabilize parsing
- hallucinate structure

### Solution
Built:
- conservative thresholds
- disagreement logic
- rule-first architecture
- conditional activation

---

## Problem 5 — Embedding Calibration

### Issue
MiniLM similarity scores were lower than expected for:
- short technical phrases
- compressed resume text

Example:

```plaintext
Python FastAPI PyTorch
```

initially produced weak confidence.

### Solution
Improved:
- semantic prototypes
- threshold calibration
- keyword-rich prototype design
- margin-based confidence logic

---

# Explainability Features

Implemented:
- section confidence reporting
- rule confidence
- NLP confidence
- disagreement reporting
- repair tracking

Example:

```python
{
    "final_section": "projects",
    "rule_section": "projects",
    "nlp_section": "projects",
    "agreement": True,
    "repair_applied": False
}
```

---

# Current System Capabilities

The system now supports:

✅ Resume parsing  
✅ JD handling  
✅ Metadata extraction  
✅ Section-aware chunking  
✅ Semantic boundary repair  
✅ Conditional NLP validation  
✅ Confidence scoring  
✅ Retrieval-ready preprocessing  
✅ Explainable parsing pipeline  

---

# LinkedIn Integration Support

The platform supports LinkedIn-style candidate ingestion through structured JSON only. This includes mock LinkedIn JSON, exported profile JSON, and recruiter-uploaded structured profile data.

The LinkedIn adapter performs deterministic rule-based normalization for skills, dates, URLs, whitespace, and duplicate handling, then maps every profile into the unified candidate schema used by the existing retrieval, scoring, ranking, recruiter analytics, workflow, and export layers.

No scraping, browser automation, external LinkedIn APIs, or separate LinkedIn ranking pipeline are used. LinkedIn candidates flow through the same recruiter-safe architecture as resume candidates.

---

# Environment Stabilization Work

Major cleanup performed:
- removed LangChain ecosystem
- fixed transformer version conflicts
- stabilized sentence-transformers
- calibrated embedding pipeline

Phase 6C dependency setup:

```bash
pip install -r requirements.txt
python -m pytest
streamlit run main.py
```

Dependency notes:
- `faiss-cpu` is used for evaluator-friendly CPU vector search.
- `sentence-transformers` downloads the configured embedding model on first use.
- The default LLM provider is deterministic `mock`; OpenAI and Gemini SDKs are not required until real provider integrations are implemented.
- CUDA-specific torch wheels and local environment artifacts are intentionally excluded from `requirements.txt`.

---

# Current Architecture Quality

The preprocessing pipeline is now:

- scalable
- modular
- explainable
- retrieval-friendly
- deterministic-first
- semantically aware
- FAISS-ready

---

# NEXT PHASE

# Phase 3 — Embeddings & FAISS

Upcoming goals:
- embedding generation
- vector storage
- semantic retrieval
- candidate similarity search
- recruiter query support

---

# Long-Term Vision

Transform the system into:

# HR Resume & LinkedIn Shortlisting Agent

with:
- semantic candidate ranking
- recruiter-facing AI reasoning
- explainable recommendations
- LinkedIn enrichment
- conversational querying
- intelligent shortlisting

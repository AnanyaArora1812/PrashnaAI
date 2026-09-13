# PrashnaAI

A retrieval-augmented question-answering system built on a scanned Sanskrit/Hindi astrology text (Brihat Parashar Hora Shastra). Ask a question, get an answer grounded in the actual source pages, with citations. Runs entirely on CPU — no GPU, no API keys, no external services.

## Why this project

Most RAG demos use clean, digital-native English text. This one doesn't get that luxury:

- The source is an 800-page **scanned PDF** with no embedded text layer — every page had to go through OCR
- The text is **Devanagari script** (Sanskrit/Hindi), mixed with occasional English
- Everything runs on a **CPU-only laptop** (Intel i3, no CUDA)

Getting from a raw scanned book to a working question-answering system meant solving real problems along the way: OCR accuracy on Devanagari, memory limits during long-running extraction, a small quantized model that kept looping on itself, and retrieval quality tuning. None of it was theoretical.

## How it works
PDF → OCR extraction → text cleaning → chunking → embeddings
→ FAISS index → retrieval → LLaMA generation → cited answer


A question comes in, gets embedded and matched against the indexed chunks, and the most relevant passages are handed to a local LLaMA model along with the question. The model is instructed to answer only from that context, and the response comes back with the page numbers it drew from.

## Stack

- **OCR** — EasyOCR (Devanagari + English), with PyMuPDF for rendering PDF pages to images
- **Embeddings** — sentence-transformers, multilingual model (paraphrase-multilingual-MiniLM-L12-v2)
- **Vector search** — FAISS, cosine similarity
- **LLM** — LLaMA 3.2 1B Instruct, quantized to GGUF, run locally via llama-cpp-python
- **Config** — everything (chunk size, top-k, generation params) lives in `configs/config.yaml`, nothing hardcoded

## Project layout
src/
rag/ pdf loading, OCR, cleaning, chunking, embeddings, retrieval
models/llama/ model loading
inference/ prompt construction and generation
ask.py command-line entry point

configs/config.yaml all tunable settings
datasets/ raw PDF, OCR output, chunks, embeddings, FAISS index
models/llama_gguf/ local model file (not in repo, see setup)


## Setup

```bash
git clone https://github.com/AnanyaArora1812/PrashnaAI.git
cd PrashnaAI
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Place your source PDF in `datasets/raw/pdfs/`.

Download the LLaMA model (not included in the repo — it's ~770MB):
[Llama-3.2-1B-Instruct-Q4_K_M.gguf](https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF) → save to `models/llama_gguf/`

Run the pipeline in order:

```bash
python src/rag/extract_all_pages.py    # OCR — slow, checkpointed, safe to resume
python src/rag/build_chunks.py
python src/rag/build_embeddings.py
python src/rag/build_faiss_index.py
```

Then ask something:

```bash
python src/ask.py "मंगल ग्रह का फल"
```

## Example
Answer:
मंगल ग्रह का फल देने वाला, 15 तक मध्यम फल, इसके ऊपर 20 तक पूर्ण फल होने,
और भी अन्य ग्रहों से जोड़ लाना चाहिए...

Sources:

Brihat Parashar Hora Shastra.pdf, Page 71
Brihat Parashar Hora Shastra.pdf, Page 617
Brihat Parashar Hora Shastra.pdf, Page 69


## Status

Working end-to-end: OCR, cleaning, chunking, embeddings, FAISS retrieval, and LLaMA generation with citations are all functional and tested against the full 800-page book (average OCR confidence 0.52).

Still ahead: LoRA fine-tuning, an evaluation suite, and a Streamlit interface.

## Notes on getting this working

A few things came up that are worth mentioning for anyone trying something similar on modest hardware:

- The PDF turned out to have no text layer at all — every one of the 800 pages needed OCR, which took several hours on CPU and had to be built as a checkpointed job so a crash or sleep interruption wouldn't lose progress.
- Image resolution and batch size for OCR needed tuning to avoid memory pressure on an 8GB machine — too aggressive a setting caused the process to swap and effectively hang.
- The first version of the LLM generation step would get stuck repeating the same phrase. Standard fix: repetition penalty and nucleus sampling.
- Chunk size and retrieval depth were tuned after the first pass produced overly fragmentary results — larger chunks with a minimum length filter improved answer quality noticeably.

## License

See [LICENSE](LICENSE).

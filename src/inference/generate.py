"""
generate.py

Phase 8b: generates a grounded answer given a question and retrieved
context chunks, using the local LLaMA model.

This is where RAG and the LLM meet: retrieved passages are inserted
into a prompt template that instructs the model to answer ONLY using
that context, reducing hallucination (per project Section 12/17).
"""

from __future__ import annotations

import logging

from models.llama.model_loader import get_llama_model

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


PROMPT_TEMPLATE = """You are PrashnaAI, an assistant that answers questions about a Sanskrit/Hindi astrology text (Brihat Parashar Hora Shastra) using ONLY the context passages provided below.

Rules:
- Answer using only the information in the context. Do not use outside knowledge.
- Write a complete, well-explained answer of 3-5 sentences, not just a single fact or list.
- If the context does not contain enough information to answer, say so clearly instead of guessing.
- The context may be in Hindi/Sanskrit (Devanagari) or English. Answer in the same language as the question.

Context:
{context}

Question: {question}

Detailed Answer:"""


def build_prompt(question, retrieved_chunks):
    context_parts = []
    for chunk in retrieved_chunks:
        context_parts.append(
            "[Source: " + chunk["source_file"] + ", Page " + str(chunk["page_number"]) + "]\n" + chunk["text"]
        )
    context = "\n\n".join(context_parts)
    return PROMPT_TEMPLATE.format(context=context, question=question)


def generate_answer(question, retrieved_chunks, model_path, max_new_tokens=512, temperature=0.3):
    model = get_llama_model(model_path)
    prompt = build_prompt(question, retrieved_chunks)

    logger.info("Generating answer (max_new_tokens=%d)...", max_new_tokens)
    result = model(
        prompt,
        max_tokens=max_new_tokens,
        temperature=temperature,
        top_p=0.9,
        repeat_penalty=1.3,
        stop=["Question:", "\n\nContext:"],
    )
    answer = result["choices"][0]["text"].strip()
    logger.info("Answer generated.")
    return answer
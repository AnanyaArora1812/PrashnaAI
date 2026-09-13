import json

with open("datasets/processed/chunks/chunks.jsonl", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total chunks: {len(lines)}\n")

# Show first 3 chunks
for line in lines[:3]:
    rec = json.loads(line)
    print(f"--- {rec['chunk_id']} (page {rec['page_number']}) ---")
    print(rec["text"][:300])
    print()
import json

with open("datasets/interim/ocr_pages.jsonl", encoding="utf-8") as f:
    for line in f:
        rec = json.loads(line)
        if rec["confidence"] < 0.3:
            print(f"Page {rec['page_number']}: confidence {rec['confidence']:.2f}, {len(rec['text'])} chars")
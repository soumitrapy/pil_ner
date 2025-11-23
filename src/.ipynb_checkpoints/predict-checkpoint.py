import json
import argparse
import torch
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
from labels import ID2LABEL, label_is_pii
import os

def validate_entity(text, start, end, label):
    """Validate entity to reduce false positives and improve precision"""
    entity_text = text[start:end].lower()
    
    # EMAIL validation
    if label == "EMAIL":
        # Must contain @ or 'at' keyword
        if "@" not in entity_text and " at " not in entity_text:
            return False
        # Should contain dot or 'dot' keyword  
        if "." not in entity_text and " dot " not in entity_text:
            return False
    
    # CREDIT_CARD validation
    elif label == "CREDIT_CARD":
        # Count digits (including spoken numbers)
        digits = re.findall(r'\d', entity_text)
        # Credit cards are 13-19 digits, be lenient for spoken form
        if len(digits) < 12:
            return False
    
    # PHONE validation
    elif label == "PHONE":
        digits = re.findall(r'\d', entity_text)
        # Phone numbers are typically 10+ digits
        if len(digits) < 10:
            return False
    
    # DATE validation
    elif label == "DATE":
        # Should contain at least one number
        if not re.search(r'\d', entity_text):
            return False
    
    # PERSON_NAME validation
    elif label == "PERSON_NAME":
        # Should be at least 2 characters
        if len(entity_text.strip()) < 2:
            return False
    
    return True


def bio_to_spans(text, offsets, label_ids):
    spans = []
    current_label = None
    current_start = None
    current_end = None

    for (start, end), lid in zip(offsets, label_ids):
        if start == 0 and end == 0:
            continue
        label = ID2LABEL.get(int(lid), "O")
        if label == "O":
            if current_label is not None:
                spans.append((current_start, current_end, current_label))
                current_label = None
            continue

        prefix, ent_type = label.split("-", 1)
        if prefix == "B":
            if current_label is not None:
                spans.append((current_start, current_end, current_label))
            current_label = ent_type
            current_start = start
            current_end = end
        elif prefix == "I":
            if current_label == ent_type:
                current_end = end
            else:
                if current_label is not None:
                    spans.append((current_start, current_end, current_label))
                current_label = ent_type
                current_start = start
                current_end = end

    if current_label is not None:
        spans.append((current_start, current_end, current_label))

    #return spans
    # Post-processing: Remove overlapping spans (keep longest)
    if not spans:
        return spans
    
    spans = sorted(spans, key=lambda x: (x[0], -(x[1] - x[0])))
    filtered = []
    last_end = 0
    
    for s, e, lab in spans:
        if s >= last_end:
            filtered.append((s, e, lab))
            last_end = e
    
    return filtered


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_dir", default="out")
    ap.add_argument("--model_name", default=None)
    ap.add_argument("--input", default="data/dev.jsonl")
    ap.add_argument("--output", default="out/dev_pred.json")
    ap.add_argument("--max_length", type=int, default=256)
    ap.add_argument(
        "--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_dir if args.model_name is None else args.model_name)
    model = AutoModelForTokenClassification.from_pretrained(args.model_dir)
    model.to(args.device)
    model.eval()

    results = {}

    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            text = obj["text"]
            uid = obj["id"]

            enc = tokenizer(
                text,
                return_offsets_mapping=True,
                truncation=True,
                max_length=args.max_length,
                return_tensors="pt",
            )
            offsets = enc["offset_mapping"][0].tolist()
            input_ids = enc["input_ids"].to(args.device)
            attention_mask = enc["attention_mask"].to(args.device)

            with torch.no_grad():
                out = model(input_ids=input_ids, attention_mask=attention_mask)
                logits = out.logits[0]
                pred_ids = logits.argmax(dim=-1).cpu().tolist()

            spans = bio_to_spans(text, offsets, pred_ids)
            ents = []
            for s, e, lab in spans:
                ents.append(
                    {
                        "start": int(s),
                        "end": int(e),
                        "label": lab,
                        "pii": bool(label_is_pii(lab)),
                    }
                )
                # Validate entity to improve precision
                if validate_entity(text, s, e, lab):
                    ents.append(
                        {
                            "start": int(s),
                            "end": int(e),
                            "label": lab,
                            "pii": bool(label_is_pii(lab)),
                        }
                    )
            results[uid] = ents

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Wrote predictions for {len(results)} utterances to {args.output}")


if __name__ == "__main__":
    main()

"""
Combine original and synthetic data for better train/dev split
"""
import json
import random
import argparse
from pathlib import Path

def load_jsonl(path):
    """Load JSONL file"""
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data

def save_jsonl(data, path):
    """Save JSONL file"""
    with open(path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def analyze_dataset(data):
    """Print dataset statistics"""
    label_counts = {}
    pii_count = 0
    non_pii_count = 0
    
    PII_LABELS = {"CREDIT_CARD", "PHONE", "EMAIL", "PERSON_NAME", "DATE"}
    
    for item in data:
        for entity in item.get('entities', []):
            label = entity['label']
            label_counts[label] = label_counts.get(label, 0) + 1
            if label in PII_LABELS:
                pii_count += 1
            else:
                non_pii_count += 1
    
    print(f"  Total utterances: {len(data)}")
    print(f"  Total entities: {sum(label_counts.values())}")
    print(f"  PII entities: {pii_count}")
    print(f"  Non-PII entities: {non_pii_count}")
    print(f"  Label distribution:")
    for label, count in sorted(label_counts.items()):
        print(f"    {label}: {count}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data", help="Data directory")
    parser.add_argument("--use_generated", action="store_true", help="Include generated synthetic data")
    parser.add_argument("--train_split", type=float, default=0.9, help="Train split ratio")
    parser.add_argument("--seed", type=int, default=22, help="Random seed")
    args = parser.parse_args()
    
    random.seed(args.seed)
    
    data_dir = Path(args.data_dir)
    
    # Load original data
    print("Loading original data...")
    train_orig = load_jsonl(data_dir / "train_original.jsonl")
    dev_orig = load_jsonl(data_dir / "dev_original.jsonl")
    
    print(f"Original train: {len(train_orig)} samples")
    print(f"Original dev: {len(dev_orig)} samples")
    
    # Combine all labeled data
    all_data = train_orig + dev_orig
    
    # Load generated data if requested
    if args.use_generated:
        train_gen_path = data_dir / "train_generated.jsonl"
        dev_gen_path = data_dir / "dev_generated.jsonl"
        
        if train_gen_path.exists() and dev_gen_path.exists():
            print("\nLoading generated data...")
            train_gen = load_jsonl(train_gen_path)
            dev_gen = load_jsonl(dev_gen_path)
            print(f"Generated train: {len(train_gen)} samples")
            print(f"Generated dev: {len(dev_gen)} samples")
            
            all_data.extend(train_gen)
            all_data.extend(dev_gen)
        else:
            print("\nGenerated data not found. Run generate_data.py first.")
            print("Proceeding with original data only...")
    
    # Shuffle
    random.shuffle(all_data)
    
    # Split
    split_idx = int(len(all_data) * args.train_split)
    train_final = all_data[:split_idx]
    dev_final = all_data[split_idx:]
    
    # Save
    train_out = data_dir / "train.jsonl"
    dev_out = data_dir / "dev.jsonl"
    
    save_jsonl(train_final, train_out)
    save_jsonl(dev_final, dev_out)
    
    print(f"\n{'='*60}")
    print("FINAL DATASET STATISTICS")
    print(f"{'='*60}")
    
    print(f"\nTrain set ({train_out}):")
    analyze_dataset(train_final)
    
    print(f"\nDev set ({dev_out}):")
    analyze_dataset(dev_final)
    
    print(f"\n✓ Saved final datasets")
    print(f"  Train: {train_out} ({len(train_final)} samples)")
    print(f"  Dev: {dev_out} ({len(dev_final)} samples)")

if __name__ == "__main__":
    main()

"""
Generate synthetic STT-style PII data for training
"""
import json
import random
from typing import List, Dict

# Templates for different entity types
FIRST_NAMES = ["ramesh", "priyanka", "rohan", "mehta", "anjali", "vikram", "neha", "amit", "shreya", "karan", 
               "pooja", "rajesh", "divya", "suresh", "kavita", "manoj", "ritu", "arun", "sneha", "deepak"]

LAST_NAMES = ["sharma", "verma", "patel", "kumar", "singh", "mehta", "gupta", "joshi", "reddy", "nair",
              "khan", "rao", "desai", "shah", "agarwal", "chopra", "malhotra", "saxena", "pandey", "iyer"]

EMAIL_DOMAINS = ["gmail", "yahoo", "outlook", "hotmail", "rediffmail"]
EMAIL_PROVIDERS = ["com", "co dot in", "in"]

CITIES = ["chennai", "mumbai", "delhi", "bangalore", "hyderabad", "pune", "kolkata", "ahmedabad", "jaipur", "lucknow"]

LOCATIONS = ["sector 5", "main street", "park avenue", "mg road", "ring road", "station road", "market street"]

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]

def number_to_words(num_str: str) -> str:
    """Convert digit to spoken form"""
    digit_map = {
        '0': ['zero', 'oh'], '1': 'one', '2': 'two', '3': 'three', '4': 'four',
        '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
    }
    words = []
    for digit in num_str:
        if digit in digit_map:
            options = digit_map[digit] if isinstance(digit_map[digit], list) else [digit_map[digit]]
            words.append(random.choice(options))
        else:
            words.append(digit)
    return ' '.join(words)

def generate_credit_card() -> Dict:
    """Generate credit card entity in STT format"""
    # Generate 16 digit card (4 groups of 4)
    groups = []
    for _ in range(4):
        group = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        groups.append(group)
    
    # Random formatting
    fmt = random.choice([
        lambda: ' '.join(groups),  # "4242 4242 4242 4242"
        lambda: ' '.join([number_to_words(g) for g in groups]),  # spoken digits
        lambda: ' '.join([groups[0], groups[1], number_to_words(groups[2]), number_to_words(groups[3])]),  # mixed
    ])
    
    text = fmt()
    templates = [
        f"my credit card number is {text}",
        f"card number is {text}",
        f"the card is {text}",
        f"credit card {text}",
    ]
    return random.choice(templates), "CREDIT_CARD", text

def generate_phone() -> Dict:
    """Generate phone number in STT format"""
    # 10 digit phone
    phone = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    
    fmt = random.choice([
        lambda: phone,  # "9876543210"
        lambda: number_to_words(phone),  # "nine eight seven..."
        lambda: f"{phone[:5]} {phone[5:]}",  # "98765 43210"
    ])
    
    text = fmt()
    templates = [
        f"call me on {text}",
        f"my number is {text}",
        f"phone is {text}",
        f"reach me at {text}",
        f"contact number {text}",
    ]
    return random.choice(templates), "PHONE", text

def generate_email() -> Dict:
    """Generate email in STT format"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    domain = random.choice(EMAIL_DOMAINS)
    ext = random.choice(EMAIL_PROVIDERS)
    
    # STT format: "john dot doe at gmail dot com"
    fmt = random.choice([
        lambda: f"{first} dot {last} at {domain} dot {ext}",
        lambda: f"{first}{last} at {domain} dot {ext}",
        lambda: f"{first} underscore {last} at {domain} dot {ext}",
    ])
    
    text = fmt()
    templates = [
        f"my email is {text}",
        f"email id is {text}",
        f"send it to {text}",
        f"email address is {text}",
    ]
    return random.choice(templates), "EMAIL", text

def generate_person_name() -> Dict:
    """Generate person name"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    
    fmt = random.choice([
        lambda: f"{first} {last}",
        lambda: f"{first} dot {last}",
        lambda: f"{first}",
    ])
    
    text = fmt()
    templates = [
        f"my name is {text}",
        f"i am {text}",
        f"this is {text}",
        f"{text} speaking",
    ]
    return random.choice(templates), "PERSON_NAME", text

def generate_date() -> Dict:
    """Generate date in STT format"""
    day = random.randint(1, 28)
    month = random.choice(MONTHS)
    year = random.randint(2020, 2025)
    
    fmt = random.choice([
        lambda: f"{day} {month} {year}",
        lambda: f"{day:02d} {random.randint(1, 12):02d} {year}",
        lambda: f"{month} {day} {year}",
    ])
    
    text = fmt()
    templates = [
        f"on {text}",
        f"date is {text}",
        f"scheduled for {text}",
        f"will travel on {text}",
    ]
    return random.choice(templates), "DATE", text

def generate_city() -> Dict:
    """Generate city (non-PII)"""
    city = random.choice(CITIES)
    templates = [
        f"i live in {city}",
        f"calling from {city}",
        f"i am in {city}",
        f"located in {city}",
    ]
    return random.choice(templates), "CITY", city

def generate_location() -> Dict:
    """Generate location (non-PII)"""
    loc = random.choice(LOCATIONS)
    city = random.choice(CITIES)
    text = f"{loc} {city}"
    templates = [
        f"address is {text}",
        f"located at {text}",
        f"office in {text}",
    ]
    return random.choice(templates), "LOCATION", text

def generate_utterance(utt_id: int) -> Dict:
    """Generate a complete utterance with multiple entities"""
    
    # Select 2-4 entity generators
    all_generators = [
        generate_credit_card,
        generate_phone,
        generate_email,
        generate_person_name,
        generate_date,
        generate_city,
        generate_location,
    ]
    
    num_entities = random.randint(2, 4)
    selected_gens = random.sample(all_generators, num_entities)
    
    # Generate parts
    parts = []
    entities_info = []
    
    for gen in selected_gens:
        part, label, entity_text = gen()
        parts.append((part, label, entity_text))
    
    # Shuffle and combine
    random.shuffle(parts)
    
    # Build full text and track entity positions
    full_text = ""
    entities = []
    
    for i, (part, label, entity_text) in enumerate(parts):
        # Add connector
        if i > 0:
            connector = random.choice([" and ", " also ", " ", " my "])
            full_text += connector
        
        # Find where entity appears in this part
        start_in_part = part.lower().find(entity_text.lower())
        if start_in_part != -1:
            # Add the part
            entity_start = len(full_text) + start_in_part
            full_text += part
            entity_end = entity_start + len(entity_text)
            
            entities.append({
                "start": entity_start,
                "end": entity_end,
                "label": label
            })
        else:
            # Fallback: just add the part
            full_text += part
    
    return {
        "id": f"utt_{utt_id:04d}",
        "text": full_text,
        "entities": entities
    }

def generate_dataset(num_samples: int, start_id: int = 0) -> List[Dict]:
    """Generate multiple synthetic utterances"""
    dataset = []
    for i in range(num_samples):
        utt = generate_utterance(start_id + i)
        dataset.append(utt)
    return dataset

def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_samples", type=int, default=1000, help="Number of training samples")
    parser.add_argument("--dev_samples", type=int, default=200, help="Number of dev samples")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output_dir", type=str, default="data", help="Output directory")
    args = parser.parse_args()
    
    random.seed(args.seed)
    
    # Generate datasets
    print(f"Generating {args.train_samples} training samples...")
    train_data = generate_dataset(args.train_samples, start_id=1)
    
    print(f"Generating {args.dev_samples} dev samples...")
    dev_data = generate_dataset(args.dev_samples, start_id=args.train_samples + 1)
    
    # Save
    train_path = f"{args.output_dir}/train.jsonl"
    dev_path = f"{args.output_dir}/dev.jsonl"
    
    with open(train_path, "w", encoding="utf-8") as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    with open(dev_path, "w", encoding="utf-8") as f:
        for item in dev_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    print(f"✓ Saved {len(train_data)} training samples to {train_path}")
    print(f"✓ Saved {len(dev_data)} dev samples to {dev_path}")
    
    # Show sample
    print("\nSample utterance:")
    print(json.dumps(train_data[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

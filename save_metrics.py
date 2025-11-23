#!/usr/bin/env python3
"""Save evaluation and latency metrics to text file"""

import subprocess
import sys
from datetime import datetime

def main():
    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = "results.txt"
    
    header = f"""=====================================================================
PII NER Model Evaluation Results
Generated: {datetime.now()}
=====================================================================
"""
    
    print(header)
    with open(output_file, 'w') as f:
        f.write(header + "\n")
    
    # Run evaluation metrics
    print("EVALUATION METRICS (Span F1)")
    print("-" * 69)
    
    with open(output_file, 'a') as f:
        f.write("\nEVALUATION METRICS (Span F1)\n")
        f.write("-" * 69 + "\n")
    
    eval_cmd = [
        "python", "src/eval_span_f1.py",
        "--gold", "data/dev.jsonl",
        "--pred", "out/dev_pred.json"
    ]
    
    process = subprocess.Popen(eval_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    with open(output_file, 'a') as f:
        for line in process.stdout:
            print(line, end='')
            f.write(line)
    process.wait()
    
    # Run latency metrics
    print("\n" + "=" * 69)
    print("LATENCY METRICS")
    print("-" * 69)
    
    with open(output_file, 'a') as f:
        f.write("\n" + "=" * 69 + "\n")
        f.write("LATENCY METRICS\n")
        f.write("-" * 69 + "\n")
    
    latency_cmd = [
        "python", "src/measure_latency.py",
        "--model_dir", "out",
        "--input", "data/dev.jsonl",
        "--runs", "50"
    ]
    
    process = subprocess.Popen(latency_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    with open(output_file, 'a') as f:
        for line in process.stdout:
            print(line, end='')
            f.write(line)
    process.wait()
    
    # Footer
    footer = f"""
=====================================================================
Results saved to: {output_file}
=====================================================================
"""
    print(footer)
    with open(output_file, 'a') as f:
        f.write(footer)

if __name__ == "__main__":
    main()

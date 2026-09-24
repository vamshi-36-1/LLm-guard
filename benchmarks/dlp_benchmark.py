import argparse
import statistics
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"dlp"))
from redactor import DLPRedactor

def main():
    p=argparse.ArgumentParser(); p.add_argument("--requests", type=int, default=200); args=p.parse_args()
    d=DLPRedactor(); samples=[]
    text="Contact alice@example.com; API key sk-abcdefghijklmnopqrstuvwxyz123456; DOB 01/02/1990."
    d.redact(text) # warm-up
    for _ in range(args.requests):
        t=time.perf_counter(); d.redact(text); samples.append((time.perf_counter()-t)*1000)
    samples.sort(); p95=samples[int(0.95*len(samples))-1]
    print(f"requests={len(samples)}")
    print(f"mean_ms={statistics.mean(samples):.2f}")
    print(f"median_ms={statistics.median(samples):.2f}")
    print(f"p95_ms={p95:.2f}")
    print("target=<50ms per request (record actual result; do not treat this script as a guarantee)")

if __name__=="__main__": main()

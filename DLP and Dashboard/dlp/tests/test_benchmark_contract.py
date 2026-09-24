from time import perf_counter
from redactor import DLPRedactor

def test_single_request_is_reasonably_bounded():
    d=DLPRedactor()
    start=perf_counter(); d.redact("Contact alice@example.com and call +1 555 123 4567"); elapsed=(perf_counter()-start)*1000
    # Generous test guard; the official <50 ms target is evaluated by benchmarks/dlp_benchmark.py.
    assert elapsed < 2000

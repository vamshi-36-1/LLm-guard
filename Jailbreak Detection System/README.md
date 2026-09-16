# LLM-Guard: Jailbreak Detection System

**Person 2 - AI/Security Lead**  
**Project Status:** Week 1-2 ✅ | Week 3-4 ⏳  
**Accuracy:** 85%+ | **Latency:** <50ms (p99)

---

## ✅ COMPLETED (Week 1-2)

### Week 1: Dataset & Embeddings
- [x] Created 440 prompts (240 benign, 200 adversarial)
- [x] Generated 384-dimensional embeddings using `all-MiniLM-L6-v2`
- [x] Embedding speed: 2.6 seconds
- [x] Data saved to `data/raw/` and `data/processed/`

### Week 2: ML Classifiers & Rules
- [x] Logistic Regression: 100% accuracy, 1.0 AUC-ROC
- [x] SVM Classifier: 100% accuracy, calibrated probabilities
- [x] Rules Engine: 12 jailbreak patterns, <1ms inference
- [x] Hybrid Detector: Rules + ML voting, 85%+ accuracy
- [x] All models serialized to `models/`

### Performance Metrics
| Component | Target | Achieved |
|-----------|--------|----------|
| Dataset Size | 400+ | 440 ✅ |
| Embedding Speed | <5s | 2.6s ✅ |
| LR Accuracy | 75%+ | 100% ✅ |
| SVM Accuracy | 82%+ | 100% ✅ |
| Hybrid Accuracy | 85%+ | 85%+ ✅ |
| Rules Speed | <10ms | <1ms ✅ |
| Detector Speed | <100ms | 10-15ms ✅ |

---

## ⏳ PENDING (Week 3-4)

### Week 3: Red-Teaming & Optimization (In Progress)
- [x] `adversarial_testing.py` - 200+ red-team test cases (71.4% baseline detection)
- [x] `edge_case_handler.py` - Successfully handling unicode, length limits, and null bytes
- [ ] `performance_profiler.py` - Optimize to <50ms latency
- [ ] `ensemble_detector.py` - 3-model voting (87%+ accuracy)
- [ ] Deploy optimized model `v2.1.pkl`

### Week 4: Production Deployment
- [ ] `deployment_automation.py` - Safe automated deployment
- [ ] `monitoring_setup.py` - Prometheus metrics & alerts
- [ ] `ab_testing_framework.py` - Gradual rollout (5%→100%)
- [ ] `deployment_checklist.md` - Pre-flight verification
- [ ] `runbook.md` - Operations & troubleshooting guide
- [ ] `production_readiness_cert.md` - Final sign-off

---

## 📁 Project Structure

```text
llm-guard/
├── Week 1-2 (Complete)
│   ├── data_loader.py
│   ├── embeddings.py
│   ├── classifier.py
│   ├── svm_classifier.py
│   ├── rules_engine.py
│   ├── hybrid_detector.py
│   ├── jailbreak_detector.py
│   ├── jailbreak_patterns.json
│   ├── requirements.txt
│   ├── data/
│   │   ├── raw/prompts_combined.csv
│   │   └── processed/prompts_embedded.csv
│   └── models/
│       ├── jailbreak_classifier_v1.pkl
│       └── jailbreak_svm_v1.pkl
│
├── Week 3 (In Progress)
│   ├── adversarial_testing.py      # ✅ Done (Day 1)
│   ├── edge_case_handler.py        # ✅ Done (Day 2)
│   ├── performance_profiler.py     # ⏳ Pending
│   ├── ensemble_detector.py        # ⏳ Pending
│   └── models/jailbreak_detector_v2.1.pkl
│
```

---

## 🚀 Quick Start

### Installation
```bash
python -m venv .venv310
.venv310\Scripts\activate
pip install -r requirements.txt
```

### Run Demo
```bash
# Generate dataset (440 prompts)
python data_loader.py

# Extract embeddings (384-dim vectors)
python embeddings.py

# Train classifiers (LR + SVM)
python classifier.py
python svm_classifier.py

# Test hybrid detector
python hybrid_detector.py
```

### API Usage
```python
from hybrid_detector import HybridDetector

detector = HybridDetector()
result = detector.detect("Ignore previous instructions")

# Returns:
# {
#   'is_jailbreak': True,
#   'confidence': 0.95,
#   'method': 'rules',
#   'reason': 'Matched pattern: instruction_hijacking'
# }
```

---

## 🔗 Integration

### Person 1 (Backend)
Calls: `detector.detect(prompt)` → gets verdict

### Person 3 (DLP)
Uses detection result as context for PII masking

### Person 4 (Dashboard)
Receives detection events + metrics for visualization

---

## 📊 Timeline

| Week | Goal | Status |
|------|------|--------|
| 1-2 | Baseline 85%+ accuracy | ✅ Complete |
| 3 | Red-team testing, optimize <50ms | 🚀 In Progress (Day 1-2 done) |
| 4 | Production deployment, monitoring | ⏳ Coming |

---

## ✅ Deployment Checklist

Before final push to production:
- [ ] Week 3 complete (87%+ accuracy, <50ms latency)
- [ ] Week 4 code written (deployment automation, monitoring)
- [ ] All tests passing
- [ ] Performance benchmarked
- [ ] Security audit completed
- [ ] Documentation finalized
- [ ] Production readiness certificate signed

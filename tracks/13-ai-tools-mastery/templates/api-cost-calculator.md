# Cloud API vs. Local GPU Cost Calculator

Use this reference sheet to model monthly API credit spend vs. local GPU workstation hardware amortization payback periods.

---

## 📊 Monthly Volume & Cost Modeling

| Monthly Volume (Renders) | Avg. API Cost / Render | Monthly Cloud API Spend | Local GPU Rig Cost (RTX 4090) | Local Hardware Payback Period |
|---|---|---|---|---|
| **100 Renders / mo** | $0.06 | **$6.00 / mo** | $2,500 | 416 Months (Not Recommended) |
| **500 Renders / mo** | $0.06 | **$30.00 / mo** | $2,500 | 83 Months |
| **2,500 Renders / mo** | $0.06 | **$150.00 / mo** | $2,500 | **16.6 Months** |
| **10,000 Renders / mo** | $0.06 | **$600.00 / mo** | $2,500 | **4.1 Months (Highly Recommended)** |

---

## 💡 Architecture Recommendation Thresholds

```
Monthly Render Volume?
├── < 1,500 Renders / mo ──► Use Cloud APIs (muapi / Replicate) — Zero upfront hardware cost
├── 1,500 - 5,000 Renders ──► Hybrid Model (RunPod Cloud GPUs for heavy batch runs)
└── > 5,000 Renders / mo  ──► Buy Local GPU Workstation (RTX 4090 24GB VRAM) — $0 marginal cost
```

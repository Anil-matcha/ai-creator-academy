# AI Tool Evaluation Framework Checklist

Use this 5-point evaluation framework to test and score new AI models before integrating them into production client workflows.

---

## 🔍 5-Point Tool Evaluation Checklist

### 1. Photorealism & Micro-Detail Fidelity (Weight: 25%)
- [ ] **Skin Pores & Anatomy:** Does the model maintain natural skin texture without waxy/plastic smoothing?
- [ ] **Lighting Falloff:** Do highlights and shadows behave realistically across complex surfaces?

### 2. Prompt Adherence & Spatial Control (Weight: 25%)
- [ ] **Multi-Subject Placement:** Does the model respect positional instructions (left, right, background, foreground)?
- [ ] **Text Legibility:** Can the model render clean, un-garbled typography when prompted?

### 3. Identity & Geometry Stability (Weight: 20%)
- [ ] **Face Vector Retention:** Does identity locking remain consistent across 5 consecutive generations?
- [ ] **I2V Temporal Stability:** Does Image-to-Video generation prevent morphing distortion?

### 4. API Speed & Developer Experience (Weight: 15%)
- [ ] **Inference Speed:** Does the render complete within acceptable SLA thresholds (< 30 sec)?
- [ ] **API Reliability:** Is the uptime and response rate above 99.5%?

### 5. Unit Economics & Pricing Model (Weight: 15%)
- [ ] **Margin Protection:** Does the cost-per-render allow for at least a 70%+ gross margin on client packages?
- [ ] **Commercial Rights:** Does the provider grant full commercial licensing for generated assets?

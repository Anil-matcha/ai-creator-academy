# Vibe-Coding Session Brief Template

Use this brief to plan each coding session before opening your agent. Completing this sheet takes 8–10 minutes and prevents session confusion.

---

## 🗂️ Session Details

* **Date:** `[YYYY-MM-DD]`
* **Tool Name:** `[e.g., FLUX Batch Prompt Runner]`
* **Session Goal:** `[e.g., Build a working v1.0 and verify it runs on 10 prompts]`
* **Agent Platform:** `[ ] Claude Code  [ ] Cursor  [ ] Windsurf  [ ] Other: ___`
* **Target Session Length:** `[e.g., 60 minutes]`

---

## 📋 Tool Specification

### One-Sentence Description
> `[Tool Name] reads [INPUT] and produces [OUTPUT] by [TRANSFORMATION].`

*Example: "This tool reads a list of product names from `products.txt` and produces `seo_titles.csv` containing 3 SEO-optimized Etsy listing titles and 5 keywords per product, generated using GPT-4o-mini."*

### Input Definition
* **Input File Name:** `[e.g., products.txt]`
* **Input Format:** `[e.g., Plain text, one product name per line]`
* **Example Input Row:** `[e.g., "Cyberpunk Cat Tee"]`

### Output Definition
* **Output File Name:** `[e.g., seo_titles.csv]`
* **Output Format:** `[e.g., CSV with columns: ProductName, Title1, Title2, Title3, Keywords]`
* **Example Output Row:** `[e.g., "Cyberpunk Cat Tee","Cyberpunk Cat Shirt for Gamers","Neon Cat Anime T-Shirt","Futuristic Cat Graphic Tee","cyberpunk,anime,cat,gamer,neon"]`

### Transformation
* **API / Service Used:** `[e.g., OpenAI GPT-4o-mini / muapi /nano-banana-2 / None (local logic)]`
* **API Key Storage:** `[e.g., Environment variable OPENAI_API_KEY]`
* **Core Prompt / Logic:** `[Paste the system prompt or describe the transformation logic]`

---

## ⚠️ Error Handling Rules

List how the tool should behave when things go wrong:
* Blank or empty input lines: `[e.g., Skip silently and continue]`
* API rate limit or timeout: `[e.g., Retry once after 5 seconds, then log to errors.log]`
* Invalid file format: `[e.g., Print a clear error message and exit]`

---

## 🔧 Technical Constraints

* **Allowed packages:** `[e.g., openai, requests, csv (standard library) — no additional installs]`
* **Python version:** `[e.g., 3.10+]`
* **Output encoding:** `[e.g., UTF-8]`
* **Max input size to handle:** `[e.g., Up to 500 rows without timeout]`

---

## ✅ Definition of Done (Phase 3 Test Checklist)

Check these before moving to Phase 4 — SHIP:

- [ ] Runs without errors on a real 10-row input file.
- [ ] Output file contains the correct number of rows (1 per input line).
- [ ] Output format matches the specification exactly.
- [ ] Handles at least 1 edge case (blank line, special character, or long string).
- [ ] Completes in under 60 seconds for a 50-row input.
- [ ] Error messages are clear and human-readable.

---

## 📦 Phase 4 — SHIP Checklist

Ask the agent to generate these packaging files before zipping:

- [ ] `README.md` — Installation steps, usage instructions (no assumed knowledge).
- [ ] `requirements.txt` — All pip-installable packages.
- [ ] `sample_input.[ext]` — A real example input file buyers can test immediately.
- [ ] `sample_output.[ext]` — The expected output from the sample input.
- [ ] Version tag in README: `v1.0 — [Release Date]`

---

## 📝 Session Log (Fill In During Session)

| Phase | Status | Notes |
|---|---|---|
| Prompt (Brief) | ⬜ / ✅ | |
| Build (Agent First Draft) | ⬜ / ✅ | |
| Test (Real Data Run) | ⬜ / ✅ | Errors encountered: |
| Ship (README + Zip) | ⬜ / ✅ | |

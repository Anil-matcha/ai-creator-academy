# Singing Voice Conversion Brief

Use this brief to configure and audit vocal timber transfer runs using singing voice conversion (SVC) engines (like RVC or local So-Vits-SVC builds).

---

**Project Title:** ________________________  
**Source Vocalist (Input Track):** ________________________  
**Target Voice Model:** ________________________  

## 1. Input Vocal Preparation

- [ ] **Acapella Extraction:** Extract vocal track from original song instrumentals using AI stem splitters (e.g. Demucs or Lalal.ai).
- [ ] **Pitch & Tuning Alignment:** Run auto-tune (or pitch correction) on the source vocal *before* conversion. Model engines transfer timbre, but struggle to fix out-of-tune notes.
- [ ] **Dynamic Compression:** Smooth out extreme volume spikes so the converter receives a steady input level.

## 2. Model Conversion Parameters

* **Pitch Shift (Transpose):** `________` semitones.
  * *Rule of Thumb:* Set to `0` if source and target have matching vocal ranges. Shift by `+12` (up one octave) if converting male to female voice; shift by `-12` if converting female to male.
* **Feature Retrieval Index Rate:** `________` (Standard: 0.6 to 0.8. Higher preserves target voice identity; lower allows more expressive inflection from the source).
* **Protect Voiceless Consonants:** `________` (Standard: 0.33 to protect "s", "t", "p" sounds from digital artifacts).

---

## 3. Conversion Quality Log

Audit the output audio file for synthesis glitches:

| Run # | Pitch Shift | Index Rate | Breathing Sounds (Pass/Fail) | Digital Rasps / Artifacts | Audit Status |
|---|---|---|:---:|---|---|
| **01** | +12 semitones | 0.75 | Pass | Slight rasp on high notes | Fail - needs pitch adjustment |
| **02** | +10 semitones | 0.65 | Pass | None, clean conversion | **Pass - Final Master** |
| | | | | | |

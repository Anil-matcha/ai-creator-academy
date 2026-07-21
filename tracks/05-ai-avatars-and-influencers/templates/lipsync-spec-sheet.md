# Lip-Sync Specification Sheet

Use this sheet to prep your audio and video assets before feeding them into lip-sync engines (e.g. Sync-Lipsync, Volcengine, or Veed-Lipsync) to prevent mouth warping and sync drift.

---

**Project Name:** ________________________  
**AI Character:** ________________________  

## 1. Input Asset Requirements

- [ ] **Base Video File (Anchor Headshot):**
  * Aspect Ratio: Vertical `9:16` (1080 x 1920) or Square `1:1`.
  * Subject Position: The face must be completely facing the camera, centered, with the mouth closed and clear of shadows.
  * Movement: Zero high-speed head turns or hand obstructions near the mouth.
- [ ] **Narration Audio File:**
  * Format: Clean `.wav` or high-quality `.mp3`.
  * Noise Gate: Strip out background hiss, music, or breathing noises.
  * Spacing: Ensure at least **0.5 seconds** of silence at the start and end of the audio file to allow the mouth anchor to transition naturally.

## 2. Sync Pacing Log

Track alignment milestones on the timeline during rendering:

| Dialogue Line | Audio File | Video Template | Duration (s) | Warping Grade (Pass/Fail) | Sync Drift (ms) |
|---|---|---|:---:|:---:|---|
| "Hey, it's [Name] here. Today we are..." | `01_intro.mp3` | `avatar_intro.mp4` | 4.5s | | |
| "If you want to automate invoice..." | `02_solve.mp3` | `avatar_body.mp4` | 8.2s | | |
| | | | | | |

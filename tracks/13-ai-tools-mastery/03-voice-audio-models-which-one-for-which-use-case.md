# Voice/Audio Models — Which One for Which Use Case

> Select the right audio stack: ElevenLabs, Suno v3.5, Udio, Bark, and Whisper speech-to-text.

**Track:** AI Tools Mastery  
**Time:** ~35 minutes  
**Prerequisites:** [01: Image Models](01-image-models-which-one-for-which-use-case.md), [02: Video Models](02-video-models-which-one-for-which-use-case.md)  

## The Problem

Audio quality makes or breaks video production. Studies show viewers tolerate mediocre video resolution, but immediately click away from bad audio or robotic voiceovers.

Creators struggle with choosing audio AI models:
* Using low-end TTS engines results in monotone, robotic voiceovers with unnatural pacing.
* Generating full music tracks with vocals when the scene only needed ambient background instrumentals destroys dialogue clarity.
* Attempting voice cloning without noise-cleaned reference audio produces distorted audio artifacts.

You need an exact tool mapping strategy for voice synthesis, music generation, and audio stem isolation.

---

## The Concept

The **Complete Audio Stack Pipeline** separates speech, music, and sound effects (SFX):

```
Text Script ──► ElevenLabs Voice Synthesis ──► Suno/Udio Instrumental Track ──► Audio Stem Mix & Mastering
```

### The 3 Pillars of AI Audio:

1. **Voice Synthesis & Cloning (ElevenLabs / Bark):** High-emotional-range voiceovers, voice cloning, and multilingual translation with natural breath pacing.
2. **Generative Music & Score Composition (Suno v3.5 / Udio):** Full-length cinematic soundtracks, commercial background beats, and genre-specific music scores.
3. **Speech-to-Text & Subtitle Automation (Whisper):** Highly accurate transcription, timestamp alignment, and automated open-caption generation.

---

## Do It

### Step 1: Match Audio Requirements to Brief
Open [`templates/video-audio-stack-matrix.md`](templates/video-audio-stack-matrix.md). Map your audio needs:
* **Narration & Commercial Voiceover:** **ElevenLabs Multilingual v2** (High emotional dynamics, stability `0.45`, clarity `0.85`).
* **Cinematic Film Score / Background Beat:** **Suno v3.5** (Instrumental prompt mode) or **Udio**.
* **Subtitle & Transcript Generation:** **OpenAI Whisper** (Large-v3 model).

### Step 2: Configure Voice Synthesis Parameters
In ElevenLabs:
* Set **Stability** to `0.40 - 0.50` for expressive, natural voice modulation.
* Set **Clarity + Similarity Boost** to `0.80` for clean studio presence.

### Step 3: Mix Dialogue & Music Stems
Ensure background music is ducked by **-14dB** below the voiceover narration track during video editing.

---

## Worked Example

**Audio Production Pipeline for "Commercial Real Estate Ad"**

* **Voiceover:** ElevenLabs "Adam - Deep Corporate Narrator" (Stability `0.45`).
* **Background Score:** Suno v3.5 Instrumental (`"Ambient corporate piano, warm uplifting strings, 110 bpm"`).
* **Transcription:** OpenAI Whisper auto-generated SRT subtitles.
* **Production Time:** 8 minutes total.
* **Total Audio Cost:** **$0.12** credit cost vs. **$400** voice actor + stock music license.

---

## Compare Tools

| Model / Platform | Primary Category | Strengths | Best For |
|---|---|---|---|
| **ElevenLabs** | Voice Synthesis & Cloning | Emotional dynamics, multi-speaker dialogue, voice cloning | Commercial voiceovers, audiobooks, podcasts |
| **Suno v3.5** | Generative Music | Full song structure (Verses, Chorus), fast generation | Background music tracks, jingles, scores |
| **Udio** | Generative Music | Superior fidelity and vocal mix control | High-fidelity music production & stems |
| **Whisper (OpenAI)** | Speech-to-Text | 99%+ transcription accuracy across 50+ languages | Video subtitles, transcripts, closed captions |

---

## Launch It

* **Always Use Clean Reference Audio for Voice Cloning:** Provide at least 3 minutes of background-noise-free, 44.1kHz studio WAV audio when creating custom client voice clones.

---

## Exercises

1. **Easy:** Generate a 30-second commercial voiceover script using ElevenLabs.
2. **Medium:** Create an instrumental background track using Suno v3.5 matching your voiceover tempo.
3. **Hard:** Produce a complete audio mix (Voiceover + Music + Subtitles) for a 60-second video ad.

---

## Templates

* [`templates/video-audio-stack-matrix.md`](templates/video-audio-stack-matrix.md) — Voice parameter setups, music prompt structures, and stem mixing checklists.

---

[← Video Models](02-video-models-which-one-for-which-use-case.md) · Next: [API vs. Local: A Decision Framework →](04-api-vs-local-decision-framework.md)

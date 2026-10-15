# Track 6 — AI Audio & Music

> Voice cloning, translation, dubbing, podcast production, and AI music — the track every video track quietly depends on.

Five modules, in order. Each is one markdown file — click straight in, no subfolders. Every module follows the same structure: Problem → Concept → Do It → Compare Tools → Launch It → Exercises.

**"Templates" below** = the reusable template(s) each module produces (specs sheets, checklists, libraries) — actual files you fill in and reuse, saved in [`templates/`](templates/).

| # | Module | Time | Requires |
|:---:|---|:---:|---|
| 1 | [Voice Cloning & TTS Basics](01-voice-cloning-tts.md) | ~40 min | — |
| 2 | [AI Dubbing & Translation](02-dubbing-translation.md) | ~45 min | Module 1 |
| 3 | [Podcast Production & Audio Cleaning](03-podcast-production.md) | ~35 min | — |
| 4 | [AI Music & Sound Effects](04-music-sfx-generation.md) | ~35 min | — |
| 5 | [Singing Voice Conversion & Vocal Synthesis](05-singing-vocal-synthesis.md) | ~30 min | Module 1 |

---

### 1. [Voice Cloning & TTS Basics](01-voice-cloning-tts.md)

> A computer reads text; a clone reads the room.

- Train custom high-fidelity voice profiles on ElevenLabs using clean, dry speech samples.
- Configure stability and clarity sliders to enable natural expression without digital distortion.
- Record training audio in isolated environments using cardioid condenser microphones.

**Templates:** [`voice-cloning-spec.md`](templates/voice-cloning-spec.md)

### 2. [AI Dubbing & Translation](02-dubbing-translation.md)

> A video that speaks only one language reaches only a fraction of the world.

- Dub and translate narratives into multiple target languages while keeping original speaker voice timber.
- Compress speech speed programmatically to fit foreign phrases into strict visual time boundaries.
- Localize video text descriptions and channel titles using translation checklists.

**Templates:** [`dubbing-translation-checklist.md`](templates/dubbing-translation-checklist.md)

### 3. [Podcast Production & Audio Cleaning](03-podcast-production.md)

> Bad audio is turned off; good audio is listened to for hours.

- Clean voice recordings by cutting rumble below 80Hz and gating noise floor below -48dB.
- Smooth volume peaks and compress dynamic range using standardized 3:1 compressor thresholds.
- Limit and normalize completed mono and stereo mixes to spotify loudness standards.

**Templates:** [`podcast-production-sheet.md`](templates/podcast-production-sheet.md)

### 4. [AI Music & Sound Effects](04-music-sfx-generation.md)

> The right sound turns b-roll into a movie.

- Write structured musical prompts specifying tempo (BPM), instruments, and vocal exclusions.
- Automatically lower background music levels using auto-ducking limits when narration is speaking.
- Generate clean transition swooshes and button taps in isolation.

**Templates:** [`audio-prompt-library.md`](templates/audio-prompt-library.md)

### 5. [Singing Voice Conversion & Vocal Synthesis](05-singing-vocal-synthesis.md)

> Synthesize the melody, clone the artist.

- Convert voice timbres using retrieval-based voice conversion (RVC) models.
- Correct pitch variations in guide vocal recordings using pitch snap filters before conversion.
- Adjust pitch shifting values by octaves to convert guide tracks across male and female vocal ranges.

**Templates:** [`vocal-conversion-brief.md`](templates/vocal-conversion-brief.md)

---

All templates live in [`templates/`](templates/). For status across the other 9 tracks, see [ROADMAP.md](../../ROADMAP.md).

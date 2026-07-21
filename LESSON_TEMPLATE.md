# Module Template

Every module is one `module.md` file inside `tracks/<NN>-<track-slug>/<NN>-<module-slug>/`, following this exact structure. Copy this file's shape when writing a new one.

```markdown
# [Module Title]

> [One-line motto — the core idea that sticks]

**Track:** [Track name]
**Time:** ~[estimated time]
**Prerequisites:** [prior modules needed, or "None"]

## The Problem

[2-3 paragraphs. What can't you do without this? Make it concrete — a real scenario
where not knowing this costs money or time.]

## The Concept

[Explain with plain language and diagrams where useful. No step-by-step yet —
build the mental model first: what's actually happening, why it works.]

## Do It

[Step-by-step walkthrough — the actual workflow, start to finish. Assume the
reader has muapi API access. Every step should be concrete enough to follow
without guessing.]

### Step 1: [Name]
### Step 2: [Name]
[...continue...]

## Compare Tools

[Show the tradeoffs across paths — muapi API vs. other paid tools vs. local/
self-hosted (ComfyUI, local diffusion/video/TTS) where a local option
realistically exists. Be honest about cost, speed, and quality — don't just
say "APIs are easier."]

## Launch It

[The monetization content — this is what most tutorials skip. Cover: how to
price this as a service or product, how to position it, where to find first
clients/distribution, and the real numbers (with sources) so claims are
checkable.]

## Exercises

1. [Easy — reinforce the core concept]
2. [Medium — apply it to a different case]
3. [Hard — combine with a prior module or scale it up]

## Outputs

[List the reusable artifacts this module produces, saved in this module's
`outputs/` folder — e.g. a prompt template, a pricing sheet, an outreach
script, a checklist.]
```

## Rules for every module

- Follow the six beats in order: Problem → Concept → Do It → Compare Tools → Launch It → Exercises. Don't skip "Compare Tools" or "Launch It" — they're what differentiates this from a typical "how it works" tutorial.
- **Never name specific competitor course platforms, creators, or "gurus"** as sources, even when they're the actual demand evidence — cite the pattern ("X-style income claims"), not the source.
- **Show your real numbers** wherever a monetization claim is made — cite a verifiable source or mark it as an estimate, never state an unverifiable income figure as fact.
- Every module points at an app in `app.json` (`status: "existing"` with a `repo_link`, or `status: "needed"`) — never duplicate app code inline in the module folder.

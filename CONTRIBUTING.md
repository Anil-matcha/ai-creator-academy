# Contributing

Contributions of new modules, fixes to existing ones, or new tracks are welcome.

## Adding a module to an existing track

1. Copy the structure in [LESSON_TEMPLATE.md](LESSON_TEMPLATE.md) into a new `module.md` under the right numbered folder (`tracks/<NN>-<track-slug>/<NN>-<module-slug>/`).
2. Include an `app.json` (`{"status": "existing", "repo_link": "..."}` if a working app already demonstrates this, or `{"status": "needed", "repo_link": null}` if not).
3. Add an `outputs/` folder with any reusable artifact the module produces (a template, checklist, or script).
4. Update [ROADMAP.md](ROADMAP.md) to mark the module's status.

## Proposing a new track

Open an issue describing the monetizable use case and any demand evidence (marketplace gig data, case studies, documented pricing) before writing modules — tracks are added based on real demand, not just interesting ideas.

## Content rules

- Never state an unverifiable income figure as fact — cite a source or mark it as an estimate.
- Never name specific competitor course platforms, creators, or "gurus" — describe the pattern, not the source.
- Every module must include the "Compare Tools" and "Launch It" sections — these are what differentiate this curriculum from a typical tutorial.

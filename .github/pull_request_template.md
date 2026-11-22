## What changed

<!-- Summarize the change, affected skills, and user-visible effect. -->

## Validation

- [ ] `python -m pytest`
- [ ] `python -m ruff check scripts tests`
- [ ] `python scripts/validate_skills.py --strict`
- [ ] `python scripts/check_publication.py --check`
- [ ] `python scripts/check_workflows.py`
- [ ] `python scripts/check_links.py`
- [ ] `python scripts/check_whitespace.py`
- [ ] `python scripts/check_markdown_structure.py`
- [ ] `python scripts/check_resources.py`
- [ ] `python scripts/check_skill_layout.py`
- [ ] `python scripts/check_encoding.py`
- [ ] `python scripts/smoke_test_scripts.py`
- [ ] `python scripts/apply_skill_quality.py --check`
- [ ] `python scripts/generate_agent_metadata.py --check`
- [ ] `python scripts/build_index.py --check`
- [ ] `python scripts/build_provenance.py --check`
- [ ] `python scripts/check_release_readiness.py --strict`
- [ ] `python scripts/build_public_bundle.py --output ../baoanskills-public` when publication scope changed

## Review and safety

- [ ] I reviewed the change against [`docs/SKILL_REVIEW.md`](../docs/SKILL_REVIEW.md).
- [ ] The allowlist, `skills/.gitignore`, metadata, and release lock are synchronized.
- [ ] I added or preserved author, source, license, evidence, retrieval date, and modification metadata.
- [ ] Third-party source URLs use a pinned 40-character commit and the exact upstream path.
- [ ] I did not publish `NOASSERTION` content or unrelated staging skills.
- [ ] CC BY-SA attribution and ShareAlike obligations are preserved where applicable.
- [ ] Public skills contain an explicit **Authorized use only** boundary.
- [ ] I did not include credentials, private target data, or local knowledge-base files.

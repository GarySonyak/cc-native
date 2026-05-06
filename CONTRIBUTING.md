# Contributing to cc-native

Thanks for considering a contribution. cc-native stays small on purpose — its job is to keep `.claude/` artifacts honest as Claude Code evolves, not to grow new surfaces.

## Before you open a PR

- **Open an issue first** for new features or rules. If it's a bug fix or a doc reference refresh, jump straight to a PR.
- **Run the test suite**: `make test` from the repo root. All 14 fixtures must be green.
- **Install your checkout** for manual smoke testing: `claude --plugin-dir $(pwd)`.

## Code rules

- **Python stdlib only.** The verify hook and any maintainer scripts must run on a fresh CC install with nothing extra. No `pip install` step is acceptable for shipped code.
- **Python 3.12+** is the floor.
- **PRs that change `hooks/cc-native-verify.py` MUST add a fixture** under `tests/fixtures/.claude/` covering the new behavior (one expected-pass, one expected-fail where applicable). The Makefile asserts exit codes, not message text — keep that contract.
- **Reference pages under `skills/feature-guide/references/`** should mirror the live `code.claude.com` docs at the time of the change. Note the source URL and date in your PR description if a section is non-obvious.

## Commit style

Conventional Commits (`fix:`, `feat:`, `chore:`, `docs:`, `refactor:`). Short messages, focus on the why.

## Releases

Versioning is SemVer. Maintainer-side release flow is out of scope for outside contributors.

## Reporting security issues

See [SECURITY.md](SECURITY.md). Please do not open public issues for vulnerabilities.

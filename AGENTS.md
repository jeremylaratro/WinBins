# Repository Guidelines

## Project Structure & Module Organization
- `winbins/`: Core package. `cli.py` is the entrypoint, `core.py` drives tool updates, `builders/` and `tools/` house build logic and registry metadata, and `obfuscation/` contains optional payload tweaks. `config.py` and `logging.py` centralize configuration and logging defaults.
- `tests/`: Pytest suite targeting each module; mirrors package layout for quick lookup (e.g., `test_cli.py`, `test_builders.py`).
- `binaries/`: Default output folder for compiled tools. Keep it out of commits.
- `build/`: Working directory where upstream repos are cloned and built; treat as disposable.
- `docs/OBFUSCATION_GUIDE.md`: Reference for payload hardening. `WinBins.py` remains as a legacy script; new work should prefer the `winbins` CLI.

## Build, Test, and Development Commands
- Set up a venv and install dev deps: `python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]`.
- Run the CLI (default paths `./binaries` and `./build`): `winbins --help`, `winbins --list`, `winbins -t rubeus certify`.
- Check build prerequisites only: `winbins --check-deps`.
- Run tests and coverage: `pytest` or `pytest --cov=winbins --cov-report=term-missing`.
- Lint/format: `black . && isort . && flake8 winbins tests && mypy winbins`.

## Coding Style & Naming Conventions
- Python 3.8+ with 4-space indentation and 100-character line length (Black + isort profile `black` enforced in `pyproject.toml`).
- Prefer type hints throughout; keep public functions typed.
- Modules, files, and functions use `snake_case`; classes use `PascalCase`; constants are `UPPER_SNAKE_CASE`.
- Avoid committing generated binaries or build artifacts; keep code paths deterministic and side effects explicit.

## Testing Guidelines
- Pytest naming is standardized (`test_*.py`, `Test*` classes, `test_*` functions). Mirror module names to keep coverage intuitive.
- Aim to maintain or increase coverage (branch coverage is enabled); add regression tests alongside bug fixes.
- For CLI behaviors, prefer `capsys` and temporary directories to isolate filesystem impact; mock external commands/builders.

## Commit & Pull Request Guidelines
- Use concise, present-tense subject lines (e.g., `Add builder availability checks`, `Fix obfuscation config parsing`); keep bodies focused on “what” and “why”.
- PRs should include: summary of changes, test commands run with outcomes, notes on new dependencies/config keys, and any manual verification (e.g., sample `winbins -t rubeus` run).
- Link related issues when applicable and call out risk areas (networked builds, external toolchain changes).

## Security & Configuration Tips
- Tools clone and build external repositories; do not hardcode tokens or internal URLs. Validate sources before adding new tools.
- Keep `config` files and obfuscation settings minimal and documented; prefer `docs/OBFUSCATION_GUIDE.md` for technique choices.
- Treat `build/` and `binaries/` as ephemeral; clean them before sharing branches to avoid leaking payloads or large artifacts.

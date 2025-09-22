# Repository Guidelines
## Language Rules
- All commands, file paths, and technical terms must remain in **English** for execution and code integrity.
- The **final explanation, documentation, or descriptive output must always be written in Vietnamese**, unless explicitly stated otherwise.
- Example:
  - Code command: `python run_automation_test.py` (English)
  - Final explanation to user: "Đã chạy thành công test tự động cho dự án."

## Project Structure & Modules
- Root scripts such as `main_gui.py`, `core1.py`, and scenario runners (`run_automation_test.py`, `simple_test.py`) orchestrate the desktop UI and automation flows.
- `core/` contains device, flow, and configuration managers; keep shared automation logic here so it can be reused by both GUI and headless runs.
- `ui/` holds PyQt6 widgets, logging panes, and automation controllers; update these alongside any visual changes so the GUI stays in sync with backend behaviour.
- `utils/`, `config/`, and JSON assets (`demo.json`, `phone_mapping.json`, `conversation_data.json`) provide persistence and fixtures; treat `debug_dumps/` and `dumps/` as expendable scratch spaces.

## Build & Run Commands
- `pip install -r requirements_gui.txt` prepares the GUI toolchain (PyQt6, automation libraries, formatters).
- `python main_gui.py` launches the desktop client against the live automation core.
- `python build_exe.py --build` creates a distributable Windows executable; pass `--install-deps` beforehand on fresh machines.
- `python core1.py --help` (or targeted scripts like `python add_devices_to_mapping.py`) drives CLI flows when debugging without the GUI.

## Coding Style & Naming
- Use Python 3.8+ with 4-space indentation and `snake_case` module, function, and variable names; reserve `PascalCase` for Qt widgets or classes mirroring UI forms.
- Format code before submitting: `black core ui utils` and lint with `flake8 core ui utils` to catch path issues early.
- Keep modules focused: shared business logic stays under `core`, GUI orchestration under `ui`, and data helpers inside `utils`.

## Testing Guidelines
- Sanity-check automation with `python run_automation_test.py` or focused suites such as `python test_friend_request_flow.py`; each script exits non-zero on failure.
- Prefer adding new scenario tests alongside existing `test_*.py` scripts in the repository root; mirror the descriptive suffix (e.g., `_flow`, `_fix`).
- Capture log excerpts in `debug_dumps/` when diagnosing regressions, but scrub device identifiers before sharing.

## Commit & PR Workflow
- Recent history uses terse verbs (`test 10`, `check 3`); keep brevity but add context using `scope: short summary` (example: `ui: fix device table refresh`).
- Reference related issues in the description, attach screenshots for UI changes, and note any config files touched (`config/master_config.json`, `phone_mapping.json`).
- Confirm formatting and targeted tests before opening a PR; list the commands executed so reviewers can reproduce locally.

## Configuration & Data Hygiene
- Update `config/app_config.json` and `config/master_config.json` through `core/config_manager.py` helpers to avoid drifting defaults.
- Keep large conversation fixtures compressed inside `data/` or referenced externally; avoid committing personal device dumps.
- When generating new mappings or status files, store them under `debug_dumps/` or `dumps/` and add to `.gitignore` if long-lived.

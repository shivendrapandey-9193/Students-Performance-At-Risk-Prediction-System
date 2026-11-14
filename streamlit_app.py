"""
Streamlit Community Cloud Deployment Entry Point for Student Insight AI.
Identifies the repository root, injects it into sys.path before module imports,
and reliably launches the production dashboard.
"""

from pathlib import Path
import sys
import runpy

# 1. Identify repository root directory
ROOT_DIR = Path(__file__).resolve().parent

# 2. Add repository root to sys.path before importing application modules
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# 3. Path to the existing dashboard application
DASHBOARD_SCRIPT = ROOT_DIR / "src" / "dashboard" / "app.py"

if not DASHBOARD_SCRIPT.exists():
    raise FileNotFoundError(f"Dashboard script not found at {DASHBOARD_SCRIPT}")

# 4. Launch the existing dashboard using runpy without duplicate page config
if __name__ == "__main__" or "streamlit" in sys.modules:
    runpy.run_path(str(DASHBOARD_SCRIPT), run_name="__main__")

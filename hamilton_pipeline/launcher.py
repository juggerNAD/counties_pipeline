import os
import sys
import json
import hashlib
import runpy
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import simpledialog, messagebox

# -----------------------------
# CONFIGURATION
# -----------------------------
BASE_DIR = Path(__file__).parent.resolve()
ACTIVATION_FILE = BASE_DIR / ".hamilton_activated.json"
ACTIVATION_HASH = "311266068304ec6e3c049c597f83c218a582991958e36e1683c2c4e687ea1ada"

# Paths to your scripts
SCRAPER_SCRIPT = BASE_DIR / "hamilton_scraper_autohotkey.py"
COMMISSIONER_SCRIPT = BASE_DIR / "commissioner.py"

# -----------------------------
# ACTIVATION HANDLER
# -----------------------------
def check_activation():
    """
    Checks activation file, prompts GUI for code if not activated.
    """
    if ACTIVATION_FILE.exists():
        try:
            data = json.loads(ACTIVATION_FILE.read_text())
            if data.get("activated"):
                print("Already activated.")
                return True
        except Exception:
            ACTIVATION_FILE.unlink()  # corrupted file, re-activate

    # GUI prompt
    root = tk.Tk()
    root.withdraw()  # hide main window

    code = simpledialog.askstring(
        "Activation Required",
        "Enter your activation code:",
        parent=root,
        show=None
    )

    if code is None:
        # User pressed Cancel
        sys.exit("Activation cancelled.")

    # Hash check
    code_hash = hashlib.sha256(code.encode()).hexdigest()
    if code_hash != ACTIVATION_HASH:
        messagebox.showerror("Invalid Code", "The activation code is invalid.")
        sys.exit("Invalid activation code.")

    # Save activation file
    ACTIVATION_FILE.write_text(json.dumps({"activated": True}))
    messagebox.showinfo("Activation Successful", "Activation successful! You can now run the launcher.")
    return True

# -----------------------------
# SCRIPT RUNNER
# -----------------------------
def run_script(script_path):
    """
    Run a Python script inside the same process using runpy.
    This works both when running as .py or bundled in PyInstaller.
    """
    if not Path(script_path).exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    # Use runpy to execute the module as __main__ in the same process
    runpy.run_path(str(script_path), run_name="__main__")

# -----------------------------
# MAIN LAUNCHER
# -----------------------------
def main():
    # Check activation
    check_activation()

    print("\n🚀 Running Hamilton Scraper...")
    run_script(SCRAPER_SCRIPT)
    print("\n✅ Hamilton Scraper finished.\n")

    print("🚀 Running Commissioner...")
    run_script(COMMISSIONER_SCRIPT)
    print("\n✅ Commissioner finished.")

# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Script failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Done", "Launcher finished. You can close this window.")


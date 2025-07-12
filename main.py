import multiprocessing
import sys

# This is where all your application logic and classes will live.
# We will rename your current file to this.
from app import main as run_app

if __name__ == "__main__":
    # 1. This setup MUST run first.
    multiprocessing.freeze_support()
    try:
        # Use 'spawn' for a clean process, crucial for frozen apps.
        multiprocessing.set_start_method('spawn')
    except RuntimeError:
        pass # Already set.

    # 2. Now, run the application.
    sys.exit(run_app())
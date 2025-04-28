# log_setup.py

import sys

def setup_logging():
    # Pialla il file vecchio
    with open("error.log", "w", encoding="utf-8") as f:
        pass

    # Reindirizza stderr al file, in UTF-8
    sys.stderr = open("error.log", "a", encoding="utf-8")

    # Rende anche stdout sicuro (utile se vuoi printare robe Unicode)
    sys.stdout.reconfigure(encoding="utf-8")

"""
Hakku - tool for article clustering based on word
counts in titles and keywords
"""

import sys
from . import run_files

if __name__ == "__main__":
    run_files(sys.argv[1:])

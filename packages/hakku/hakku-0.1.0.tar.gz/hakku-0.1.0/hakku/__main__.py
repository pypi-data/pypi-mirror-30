"""
Hakku - tool for article clustering based on word
counts in titles and keywords
"""

import sys
from . import run_file

if __name__ == "__main__":
    run_file(sys.argv[1:])

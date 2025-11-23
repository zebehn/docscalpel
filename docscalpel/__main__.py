"""
Entry point for running DocScalpel as a module: python -m docscalpel

This allows users to run:
    python -m docscalpel paper.pdf
    python -m docscalpel paper.pdf --types figure --output ./extracted
"""

import sys
from docscalpel.cli.main import main

if __name__ == '__main__':
    sys.exit(main())

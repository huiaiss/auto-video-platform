"""One-shot Episode Builder — thin wrapper around pipeline.py

Usage:
    python build_episode.py --ep 2 --title "文字乱码"
    python build_episode.py --ep 1 --title "手指破绽"

All pipeline logic lives in pipeline.py. This is a convenience entry point.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from pipeline import main
    main()

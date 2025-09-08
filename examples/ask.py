from __future__ import annotations
import os
import sys
from pathlib import Path

# Allow running directly
sys.path.append(str((Path(__file__).resolve().parent.parent / 'src').resolve()))

from rag import answer  # noqa: E402

if __name__ == "__main__":
    q = "What are some Italian pasta meals with tomato and garlic, and how to cook one?"
    print(answer(q, k=5))

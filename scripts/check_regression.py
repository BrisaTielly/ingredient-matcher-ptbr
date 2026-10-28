"""Fail CI when evaluated metrics regress beyond an explicit tolerance."""

from __future__ import annotations

from ingredient_matcher.regression import main

if __name__ == "__main__":
    main()

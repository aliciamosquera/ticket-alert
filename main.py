"""Thin CLI launcher for ticket-alert.

This module simply invokes :func:`alert.main` so that the original
``python main.py`` invocation continues to work for users.
"""

from __future__ import annotations

from alert import main as alert_main


if __name__ == "__main__":
    alert_main()
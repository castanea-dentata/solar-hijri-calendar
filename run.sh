#!/usr/bin/env bash
# Quick launcher: creates a venv on first run, then starts the app.
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv .venv
    ./.venv/bin/pip install --upgrade pip -q
    ./.venv/bin/pip install -r requirements.txt -q
fi

./.venv/bin/python -m shcalendar

#!/bin/bash
# YouTube Clip Extractor - GUI Launcher
# Quick launcher for the web-based GUI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║    🎬 YouTube Clip Extractor - Web GUI        ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "Starting web server..."
echo ""
echo "After server starts, open: http://localhost:5001"
echo ""

cd "$SCRIPT_DIR"
python3 web_gui.py

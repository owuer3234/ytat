#!/bin/bash
# install_app.sh - One-time setup for Ubuntu / Linux.
#
# It installs everything the tool needs and adds
# "YouTube Transcript to PDF" to your app menu, so you can open it
# like any other app. Run it once from inside this folder with:
#
#     bash install_app.sh

# Stop if any step fails.
set -e

# The folder this script is in (the tool's folder).
TOOL_FOLDER="$(cd "$(dirname "$0")" && pwd)"
cd "$TOOL_FOLDER"

echo "Setting up YouTube Transcript to PDF in: $TOOL_FOLDER"

# 1. Make sure Python's window toolkit (tkinter) and the venv tool are installed.
if ! python3 -c "import tkinter, ensurepip" 2>/dev/null; then
    echo
    echo "Installing a few missing Python parts. Please type your password if asked"
    echo "(nothing shows on screen while you type it - that's normal)."
    sudo apt update
    sudo apt install -y python3-tk python3-venv python3-pip
fi

# 2. Create the virtual environment (private space for the libraries), if needed.
if [ ! -x .venv/bin/python ]; then
    echo
    echo "Creating the virtual environment..."
    python3 -m venv .venv
fi

# 3. Install the libraries the tool needs.
echo
echo "Installing the libraries..."
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements.txt

# 4. Add the app to the app menu.
MENU_FOLDER="$HOME/.local/share/applications"
mkdir -p "$MENU_FOLDER"
cat > "$MENU_FOLDER/yt-transcript-pdf.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=YouTube Transcript to PDF
Comment=Save YouTube video transcripts as PDF files
Exec="$TOOL_FOLDER/.venv/bin/python" "$TOOL_FOLDER/yt_to_pdf_app.py"
Path=$TOOL_FOLDER
Icon=accessories-text-editor
Terminal=false
Categories=Utility;
DESKTOP

echo
echo "All done!"
echo "Press the Super (Windows) key, type 'YouTube', and click"
echo "'YouTube Transcript to PDF' to open the app."
echo
echo "Keep this folder where it is - the app runs from here."

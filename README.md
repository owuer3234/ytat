# YouTube Transcript to PDF

A small tool that takes YouTube links, downloads each video's transcript
(captions), and saves it as a clean, readable PDF named after the video title.

Each PDF contains:

- the video title
- a clickable link to the video
- the transcript, split into readable paragraphs

All PDFs are saved into a folder called **`output`**.

---

## Step 1: Install Python

You need Python 3.9 or newer.

### Windows

1. Go to <https://www.python.org/downloads/> and click the big yellow
   **Download Python** button.
2. Open the file you downloaded.
3. **Important:** at the bottom of the first screen, tick the box that says
   **"Add python.exe to PATH"**. Then click **Install Now**.
4. When it finishes, open **Command Prompt** (press the Windows key, type
   `cmd`, press Enter) and check it worked:

   ```
   python --version
   ```

   You should see something like `Python 3.12.x`.

### Mac

1. Go to <https://www.python.org/downloads/> and click **Download Python**.
2. Open the downloaded `.pkg` file and follow the installer.
3. Open **Terminal** (press `Cmd + Space`, type `Terminal`, press Enter) and
   check it worked:

   ```
   python3 --version
   ```

   You should see something like `Python 3.12.x`.

### Linux (Ubuntu)

Ubuntu already comes with Python 3. You just need to add the tools for
installing libraries. Open **Terminal** (press `Ctrl + Alt + T`) and run:

```
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

It will ask for your password (nothing appears on screen while you type it,
that's normal). Then check it worked:

```
python3 --version
```

You should see something like `Python 3.12.x`.

> **Note:** On Mac and Linux you type `python3` and `pip3`. On Windows you type
> `python` and `pip`. The examples below show both.

---

## Step 2: Download this tool

Download this project as a ZIP (on GitHub: green **Code** button →
**Download ZIP**) and unzip it somewhere easy to find, like your Desktop.
You should have a folder containing `yt_to_pdf.py`, `requirements.txt` and
this `README.md`.

---

## Step 3: Open a terminal inside the project folder

### Windows

Open the project folder in File Explorer, click in the address bar at the
top, type `cmd` and press Enter. A Command Prompt opens already inside the
folder.

Or, in Command Prompt, type `cd` followed by the folder path, for example:

```
cd %USERPROFILE%\Desktop\ytat
```

### Mac

In Terminal, type `cd ` (with a space after it), then drag the project
folder from Finder into the Terminal window, and press Enter. Or, for example:

```
cd ~/Desktop/ytat
```

### Linux (Ubuntu)

Open the project folder in the Files app, right-click on an empty space
inside it and choose **Open in Terminal**. Or type `cd` followed by the
folder path, for example:

```
cd ~/Desktop/ytat
```

---

## Step 4: Install the dependencies

This installs the two libraries the tool needs (listed in `requirements.txt`).
You only need to do this once.

**Windows:**

```
python -m pip install -r requirements.txt
```

**Mac:**

```
python3 -m pip install -r requirements.txt
```

**Linux (Ubuntu):** on Ubuntu you **must** use a virtual environment (a
private space for this project's libraries). Newer Ubuntu versions refuse
a plain `pip install` with an "externally-managed-environment" error.
Run these three lines:

```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

You'll see `(.venv)` at the start of the line when it's active.
**Every time you open a new terminal**, go to the project folder and run
`source .venv/bin/activate` again before using the tool.

<details>
<summary>Optional for Windows and Mac: use a virtual environment (keeps things tidy)</summary>

A virtual environment keeps this project's libraries separate from the rest
of your computer. It is optional, but recommended.

**Windows:**

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

**Mac:**

```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

You'll see `(.venv)` at the start of the line when it's active. Run the
`activate` line again each time you open a new terminal.

</details>

---

## Step 5: Run the tool

### One video

**Windows:**

```
python yt_to_pdf.py https://www.youtube.com/watch?v=jNQXAC9IVRw
```

**Mac / Linux:**

```
python3 yt_to_pdf.py "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

> **Tip:** On Mac and Linux, put links in quotes `"..."`. Some links contain `?` or `&`,
> which the terminal treats specially otherwise. Quotes work on Windows
> too.

### Several videos at once

Just put the links one after another, separated by spaces:

**Windows:**

```
python yt_to_pdf.py "https://youtu.be/jNQXAC9IVRw" "https://www.youtube.com/shorts/VIDEO_ID"
```

**Mac / Linux:**

```
python3 yt_to_pdf.py "https://youtu.be/jNQXAC9IVRw" "https://www.youtube.com/shorts/VIDEO_ID"
```

### A text file full of links

Create a text file (for example `links.txt`) in the project folder with one
link per line. Blank lines and lines starting with `#` are ignored. There's a
sample called `links_example.txt` you can copy.

```
https://www.youtube.com/watch?v=jNQXAC9IVRw
https://youtu.be/VIDEO_ID
https://www.youtube.com/shorts/VIDEO_ID
```

Then run:

**Windows:**

```
python yt_to_pdf.py links.txt
```

**Mac / Linux:**

```
python3 yt_to_pdf.py links.txt
```

You can even mix files and links: `python yt_to_pdf.py links.txt "https://youtu.be/VIDEO_ID"`

### Where are my PDFs?

In the **`output`** folder inside the project folder. Each file is named after
the video title. If a file with that name already exists, a number is added
(e.g. `My Video (2).pdf`) so nothing gets overwritten.

---

## Supported link formats

All of these work:

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/live/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID` (mobile links)
- links with extra bits on the end like `&t=30s` or `?si=...`
- just the 11-character video ID on its own

---

## What you'll see

```
Working on: https://www.youtube.com/watch?v=jNQXAC9IVRw
  Done! Saved: output/Me at the zoo.pdf

Working on: https://youtu.be/SOME_VIDEO
  Sorry, this video has no captions/transcript available. Skipping it.

Finished: 1 of 2 PDF(s) created in the 'output' folder.
```

If a video has no captions, is private, or the link is wrong, the tool prints
a friendly message and carries on with the rest of your links.

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `'python' is not recognized` (Windows) | Python wasn't added to PATH. Re-run the installer, choose **Modify**, and tick **Add Python to environment variables**. Or try `py` instead of `python`. |
| `command not found: python` (Mac / Linux) | Use `python3` instead of `python`. |
| `error: externally-managed-environment` (Linux) | Ubuntu wants you to use a virtual environment. Follow the **Linux (Ubuntu)** part of Step 4. |
| `No module named venv` / `ensurepip is not available` (Linux) | Run `sudo apt install python3-venv`, then delete the `.venv` folder and try Step 4 again. |
| `No module named 'fpdf'` or `'youtube_transcript_api'` | You skipped Step 4, or you forgot to activate your virtual environment (`source .venv/bin/activate` on Mac/Linux, `.venv\\Scripts\\activate` on Windows). Activate it, or run the install command again. |
| `can't open file 'yt_to_pdf.py'` | Your terminal isn't in the project folder. Go back to Step 3. |
| "Something went wrong ... blocked" / "IpBlocked" | YouTube sometimes blocks lots of requests in a row, or requests from cloud servers/VPNs. Wait a while and try again, or turn off your VPN. |
| Some characters show as `?` in the PDF | The tool couldn't find a font on your computer that supports those characters, so it used a basic one. |

---

## Tweaking it

Open `yt_to_pdf.py` in any text editor. Near the top you'll find a few
settings you can change:

- `OUTPUT_FOLDER` – where the PDFs go (default: `output`)
- `WORDS_PER_PARAGRAPH` – how long each paragraph is (default: `90`)
- `PREFERRED_LANGUAGES` – which transcript language to try first
  (default: English). If none of these exist, the tool uses whatever
  language the video has.

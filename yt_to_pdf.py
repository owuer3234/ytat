"""
yt_to_pdf.py - Turn YouTube video transcripts into readable PDF files.

How to use it (see README.md for the full step-by-step guide):

    python yt_to_pdf.py https://www.youtube.com/watch?v=VIDEO_ID
    python yt_to_pdf.py LINK1 LINK2 LINK3
    python yt_to_pdf.py links.txt

Every PDF is saved into a folder called "output", named after the video title.
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request

from fpdf import FPDF
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)


# The folder where all the PDFs will be saved: a folder called "output"
# right next to this file, no matter where you run the tool from.
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# Roughly how many words go into one paragraph of the PDF.
# Bigger number = longer paragraphs.
WORDS_PER_PARAGRAPH = 90

# Languages we prefer, in order. If none are available we just take
# whatever transcript the video has.
PREFERRED_LANGUAGES = ["en", "en-US", "en-GB"]

# Fonts that support lots of languages and symbols (accents, emoji-free text,
# non-English alphabets). We use the first one found on your computer.
# If none are found, we fall back to a basic built-in font.
UNICODE_FONT_CANDIDATES = [
    # Windows
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    # Mac
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
]


# ---------------------------------------------------------------------------
# Step 1: Work out the video ID from a link
# ---------------------------------------------------------------------------

def get_video_id(link):
    """
    Pull the 11-character video ID out of a YouTube link.

    Works with all of these:
        https://www.youtube.com/watch?v=jNQXAC9IVRw
        https://youtu.be/jNQXAC9IVRw
        https://www.youtube.com/shorts/jNQXAC9IVRw
        https://www.youtube.com/embed/jNQXAC9IVRw
        https://www.youtube.com/live/jNQXAC9IVRw
        jNQXAC9IVRw   (just the ID on its own)

    Returns None if no ID can be found.
    """
    link = link.strip()

    # If someone pasted just the ID, accept it as-is.
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", link):
        return link

    # Add "https://" if it's missing so the link can be read properly.
    if not link.startswith(("http://", "https://")):
        link = "https://" + link

    parsed = urllib.parse.urlparse(link)
    host = parsed.netloc.lower()
    path_parts = [part for part in parsed.path.split("/") if part]

    # Short links: https://youtu.be/VIDEO_ID
    if host.endswith("youtu.be") and path_parts:
        candidate = path_parts[0]

    # Normal links: https://www.youtube.com/watch?v=VIDEO_ID
    elif "youtube" in host and parsed.path == "/watch":
        candidate = urllib.parse.parse_qs(parsed.query).get("v", [""])[0]

    # Shorts, embeds and live links: https://www.youtube.com/shorts/VIDEO_ID
    elif "youtube" in host and len(path_parts) >= 2 and path_parts[0] in (
        "shorts", "embed", "live", "v"
    ):
        candidate = path_parts[1]

    else:
        return None

    # Make sure what we found actually looks like a video ID.
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
        return candidate
    return None


# ---------------------------------------------------------------------------
# Step 2: Get the video's title
# ---------------------------------------------------------------------------

def get_video_title(video_id):
    """
    Ask YouTube for the video's title (no API key needed).
    If that fails for any reason, just use the video ID as the title.
    """
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    oembed_url = (
        "https://www.youtube.com/oembed?format=json&url="
        + urllib.parse.quote(watch_url, safe="")
    )
    try:
        with urllib.request.urlopen(oembed_url, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("title") or video_id
    except Exception:
        return video_id


# ---------------------------------------------------------------------------
# Step 3: Download the transcript
# ---------------------------------------------------------------------------

def get_transcript_text(video_id):
    """
    Download the transcript and return it as a list of short text pieces.
    English is preferred; otherwise the first available language is used.
    """
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)

    try:
        transcript = transcript_list.find_transcript(PREFERRED_LANGUAGES)
    except NoTranscriptFound:
        # No English - just take the first transcript the video has.
        transcript = next(iter(transcript_list))

    fetched = transcript.fetch()
    return [snippet.text for snippet in fetched]


# ---------------------------------------------------------------------------
# Step 4: Turn the pieces of text into readable paragraphs
# ---------------------------------------------------------------------------

def make_paragraphs(pieces):
    """
    YouTube transcripts come as lots of tiny pieces (a few words each).
    This joins them together and splits them into paragraphs of roughly
    WORDS_PER_PARAGRAPH words, trying to break at the end of a sentence.
    """
    # Clean up each piece: remove line breaks, extra spaces and
    # sound labels like "[Music]" or "[Applause]".
    words = []
    for piece in pieces:
        piece = re.sub(r"\[[^\]]*\]", " ", piece)
        piece = piece.replace("\n", " ")
        words.extend(piece.split())

    paragraphs = []
    current = []
    for word in words:
        current.append(word)
        ends_sentence = word.endswith((".", "!", "?"))
        long_enough = len(current) >= WORDS_PER_PARAGRAPH
        way_too_long = len(current) >= WORDS_PER_PARAGRAPH * 1.5

        # Break at a sentence end once the paragraph is long enough.
        # Auto-generated captions often have no punctuation at all,
        # so we also force a break if the paragraph gets far too long.
        if (long_enough and ends_sentence) or way_too_long:
            paragraphs.append(" ".join(current))
            current = []

    # Don't forget the last few words.
    if current:
        paragraphs.append(" ".join(current))

    return paragraphs


# ---------------------------------------------------------------------------
# Step 5: Build the PDF
# ---------------------------------------------------------------------------

def safe_filename(title):
    """
    Turn a video title into a safe file name by removing characters
    that Windows and Mac don't allow in file names (like / \\ : * ? " < > |).
    """
    name = re.sub(r'[\\/:*?"<>|]', "", title)
    name = re.sub(r"\s+", " ", name).strip(" .")
    return name[:150] or "transcript"


def unique_path(folder, name):
    """
    Return "folder/name.pdf". If that file already exists, add a number
    (name (2).pdf, name (3).pdf, ...) so we never overwrite anything.
    """
    path = os.path.join(folder, name + ".pdf")
    counter = 2
    while os.path.exists(path):
        path = os.path.join(folder, f"{name} ({counter}).pdf")
        counter += 1
    return path


def set_up_font(pdf):
    """
    Pick a font for the PDF. Returns (font_name, can_show_all_characters).
    """
    for font_path in UNICODE_FONT_CANDIDATES:
        if os.path.exists(font_path):
            pdf.add_font("MainFont", "", font_path)
            return "MainFont", True
    # Built-in font: only supports basic Western European characters.
    return "Helvetica", False


def save_pdf(title, link, paragraphs, pdf_path):
    """Write the title, link and paragraphs into a nicely spaced PDF."""
    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    font, full_unicode = set_up_font(pdf)

    def clean(text):
        # With the basic built-in font, replace characters it can't draw.
        if full_unicode:
            return text
        return text.encode("latin-1", "replace").decode("latin-1")

    # Title (big text)
    pdf.set_font(font, size=18)
    pdf.multi_cell(0, 9, clean(title), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Link (small blue text you can click)
    pdf.set_font(font, size=10)
    pdf.set_text_color(0, 0, 200)
    pdf.multi_cell(0, 6, link, link=link, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # Transcript paragraphs (normal text with a gap between paragraphs)
    pdf.set_font(font, size=12)
    for paragraph in paragraphs:
        pdf.multi_cell(0, 7, clean(paragraph), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    pdf.output(pdf_path)


# ---------------------------------------------------------------------------
# Putting it all together
# ---------------------------------------------------------------------------

def process_link(link, log=print):
    """
    Do everything for one link. Returns True if a PDF was made.
    Any problem prints a friendly message instead of crashing.

    "log" is the function used to show messages. Normally that's print(),
    but the window app (yt_to_pdf_app.py) passes its own function so the
    messages appear in the window instead.
    """
    log(f"\nWorking on: {link}")

    video_id = get_video_id(link)
    if not video_id:
        log("  Sorry, that doesn't look like a YouTube video link. Skipping it.")
        return False

    try:
        pieces = get_transcript_text(video_id)
    except TranscriptsDisabled:
        log("  Sorry, this video has no captions/transcript available. Skipping it.")
        return False
    except (NoTranscriptFound, StopIteration):
        log("  Sorry, no transcript could be found for this video. Skipping it.")
        return False
    except VideoUnavailable:
        log("  Sorry, this video is unavailable (private, deleted or wrong link). Skipping it.")
        return False
    except Exception as error:
        # Anything else (no internet, YouTube blocking requests, etc.)
        log(f"  Sorry, something went wrong getting the transcript: {error}")
        log("  Skipping this video.")
        return False

    title = get_video_title(video_id)
    paragraphs = make_paragraphs(pieces)
    if not paragraphs:
        log("  Sorry, the transcript for this video is empty. Skipping it.")
        return False

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    pdf_path = unique_path(OUTPUT_FOLDER, safe_filename(title))
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        save_pdf(title, video_url, paragraphs, pdf_path)
    except Exception as error:
        log(f"  Sorry, the PDF could not be created: {error}")
        return False

    log(f"  Done! Saved: {pdf_path}")
    return True


def collect_links(arguments):
    """
    Build the list of links to process. Each argument can be a link,
    or the name of a text file containing one link per line.
    Blank lines and lines starting with # in the text file are ignored.
    """
    links = []
    for item in arguments:
        if os.path.isfile(item):
            with open(item, encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        links.append(line)
        else:
            links.append(item)
    return links


def main():
    # sys.argv holds what you typed after "python yt_to_pdf.py".
    arguments = sys.argv[1:]
    if not arguments:
        print("Please give me at least one YouTube link or a text file of links.")
        print("Example:  python yt_to_pdf.py https://youtu.be/jNQXAC9IVRw")
        print("Example:  python yt_to_pdf.py links.txt")
        sys.exit(1)

    links = collect_links(arguments)
    if not links:
        print("No links found. Is your text file empty?")
        sys.exit(1)

    successes = 0
    for link in links:
        if process_link(link):
            successes += 1

    print(f"\nFinished: {successes} of {len(links)} PDF(s) created.")
    print(f"Your PDFs are in: {OUTPUT_FOLDER}")


# This line means: only run main() when the file is run directly.
if __name__ == "__main__":
    main()

# backend/app/services/summarizer_service.py
import os
import sys
import json
import re
from datetime import datetime

from dotenv import load_dotenv
import assemblyai as aai
from moviepy import VideoFileClip

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4

# ------------------------------
# GOOGLE GEMINI
# ------------------------------
import google.generativeai as genai

# ==========================================================
# PATH SAFETY — REQUIRED FOR FASTAPI / UVICORN
# ==========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))
UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")
OUTPUT_DIR = os.path.join(BACKEND_DIR, "output_summaries")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================================
# LOAD ENV (works for uvicorn, CLI, Docker)
# ==========================================================
ENV_PATH = os.path.join(BACKEND_DIR, ".env")
load_dotenv(ENV_PATH)

# ==========================================================
# API KEYS
# ==========================================================
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not ASSEMBLYAI_API_KEY:
    raise SystemExit("❌ Missing ASSEMBLYAI_API_KEY")

aai.settings.api_key = ASSEMBLYAI_API_KEY

GEMINI_API_KEY_PRIMARY = os.getenv("GEMINI_API_KEY_PRIMARY")
GEMINI_API_KEY_FALLBACK = os.getenv("GEMINI_API_KEY_FALLBACK")

if not GEMINI_API_KEY_PRIMARY:
    raise SystemExit("❌ Missing GEMINI_API_KEY_PRIMARY")

# ==========================================================
# GEMINI MODEL
# ==========================================================
GEMINI_MODEL = "gemini-2.5-flash"

# ==========================================================
# PROMPTS — A2 MODE (NO MARKDOWN)
# ==========================================================
SYSTEM_PROMPT_SUMMARY = """
You are an expert meeting analyst.

Generate a plain text meeting summary with these exact sections:

Executive Overview
(3–4 lines of clear prose)

Main Discussion Points
(point 1)
(point 2)
(point 3)

Decisions Taken
(decision 1)

Action Items
(person — task)
(person — task)

Unresolved Questions
(question 1)

RULES:
- NO markdown symbols.
- NO **bold**, NO #, NO *, NO lists.
- NO bullets. NO "•".
- Use only plain sentences separated by newlines.
- Keep headings exactly as given (no punctuation).
"""

SYSTEM_PROMPT_FACTS = """
Extract structured meeting facts in JSON:

{
 "topics": ["topic1", ...],
 "participants": ["name", ...],
 "decisions": ["decision1", ...],
 "action_items": [
      {"assignee": "Name or Unknown", "task": "task text", "deadline": "YYYY-MM-DD or null"}
 ],
 "issues_discussed": ["topic1", ...],
 "important_quotes": ["quote1", ...]
}

Return ONLY valid JSON.
"""

SYSTEM_PROMPT_TOPIC = """
Extract the main topic of the meeting in 3–8 words.
Return ONLY the topic text, no punctuation.
"""

SYSTEM_PROMPT_SPEAKER_BREAKDOWN = """
You receive grouped meeting transcript text per speaker in JSON format.

Return a JSON array. Each element must be:
{
  "speaker": "Speaker label",
  "summary": "2 concise sentences covering what they contributed"
}

Guidelines:
- Keep summaries factual and non-redundant.
- Mention ownership of key ideas, decisions, or concerns.
- If a speaker spoke very little, capture their key point in one short sentence.
- Preserve any provided real names; otherwise keep the label (e.g., "Speaker A").
- Never invent speakers that are not in the input.
- Only return JSON, no extra commentary.
"""


# ==========================================================
# GEMINI LLM WRAPPER
# ==========================================================
def call_gemini(prompt_text, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)

        response = model.generate_content(prompt_text)

        if not response or not response.text:
            return None

        return response.text.strip()

    except Exception as e:
        print(f"⚠️ Gemini failed ({api_key[-4:]}): {e}")
        return None


def call_llm(system_prompt, user_input):
    full_prompt = system_prompt + "\n\n" + user_input

    # 1. Primary
    if GEMINI_API_KEY_PRIMARY:
        out = call_gemini(full_prompt, GEMINI_API_KEY_PRIMARY)
        if out:
            return out

    # 2. Fallback
    if GEMINI_API_KEY_FALLBACK:
        out = call_gemini(full_prompt, GEMINI_API_KEY_FALLBACK)
        if out:
            return out

    # 3. Hard fallback so summary_clean never crashes
    print("❌ All Gemini calls failed — using fallback summary text.")
    return "Executive Overview\nNo summary could be generated.\n\nMain Discussion Points\n(none)\n\nDecisions Taken\n(none)\n\nAction Items\n(none)\n\nUnresolved Questions\n(none)"


# ==========================================================
# TRANSCRIPTION
# ==========================================================
def transcribe_with_ai(file_path):
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        punctuate=True,
        format_text=True,
        auto_highlights=True,
        entity_detection=True,
        iab_categories=True,
    )

    print("⏳ Running transcription...")
    transcript = aai.Transcriber().transcribe(file_path, config=config)

    if transcript.status == aai.TranscriptStatus.error:
        raise Exception("AssemblyAI Error: " + transcript.error)

    return transcript


# ==========================================================
# FACT EXTRACTION
# ==========================================================
def extract_facts(text):
    out = call_llm(SYSTEM_PROMPT_FACTS, text)
    if not out:
        return {}

    try:
        return json.loads(out)
    except:
        return {"raw": out}


# ==========================================================
# TOPIC EXTRACTION
# ==========================================================
def extract_topic(text):
    out = call_llm(SYSTEM_PROMPT_TOPIC, text)
    if not out:
        return "Meeting Summary"
    return out.strip()


def clean_title_spacing(title):
    if not title:
        return title
    return re.sub(r"(?<!^)(?=[A-Z])", " ", title).strip()


# ==========================================================
# CLEAN SUMMARY TEXT (A2 MODE)
# ==========================================================
def clean_summary(text):
    if not text:
        return ""

    # Remove markdown symbols
    text = text.replace("*", "").replace("#", "")

    # Split text into lines, clean each line, then rejoin.
    # This preserves the newlines that separate bullet points.
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Replace multiple spaces/tabs *within* a line, and strip ends
        cleaned_line = re.sub(r'[ \t]+', ' ', line).strip()
        cleaned_lines.append(cleaned_line)

    # Re-assemble, filtering out any blank lines
    text = "\n".join(l for l in cleaned_lines if l)

    # Ensure headings are separated by newlines
    text = re.sub(r"(Executive Overview)", r"\n\1\n", text, flags=re.IGNORECASE)
    text = re.sub(r"(Main Discussion Points)", r"\n\1\n", text, flags=re.IGNORECASE)
    text = re.sub(r"(Decisions Taken)", r"\n\1\n", text, flags=re.IGNORECASE)
    text = re.sub(r"(Action Items)", r"\n\1\n", text, flags=re.IGNORECASE)
    text = re.sub(r"(Unresolved Questions)", r"\n\1\n", text, flags=re.IGNORECASE)
    text = re.sub(r"(Speaker Contributions)", r"\n\1\n", text, flags=re.IGNORECASE)

    # Clean up any triple newlines this may have created
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ==========================================================
# SPEAKER HELPERS
# ==========================================================
def _normalize_speaker_label(label, default_index):
    if not label:
        return f"Speaker {default_index}"

    label = str(label).strip()
    if not label:
        return f"Speaker {default_index}"

    if label.lower().startswith("speaker"):
        return label.title()

    if len(label) == 1 and label.isalpha():
        return f"Speaker {label.upper()}"

    return label


def extract_speaker_segments(transcript):
    utterances = getattr(transcript, "utterances", None)
    if not utterances:
        return {}

    segments = {}
    fallback_index = 1

    for utt in utterances:
        raw_speaker = getattr(utt, "speaker", None)
        if raw_speaker is None and isinstance(utt, dict):
            raw_speaker = utt.get("speaker")

        speaker = _normalize_speaker_label(raw_speaker, fallback_index)

        text = getattr(utt, "text", None)
        if text is None and isinstance(utt, dict):
            text = utt.get("text")

        if text:
            segments.setdefault(speaker, []).append(text.strip())

        fallback_index += 1

    return {
        speaker: " ".join(filter(None, parts)).strip()
        for speaker, parts in segments.items()
        if parts
    }


def _trim_for_prompt(content, limit=2000):
    if len(content) <= limit:
        return content
    return content[:limit].rsplit(" ", 1)[0] + " ..."


def _parse_speaker_summary_response(raw_response):
    if not raw_response:
        return []

    try:
        parsed = json.loads(raw_response)
        if isinstance(parsed, list):
            cleaned = []
            for entry in parsed:
                speaker = entry.get("speaker") if isinstance(entry, dict) else None
                summary = entry.get("summary") if isinstance(entry, dict) else None
                if speaker and summary:
                    cleaned.append({
                        "speaker": speaker.strip(),
                        "summary": summary.strip()
                    })
            return cleaned
    except Exception:
        return []

    return []


def _fallback_speaker_summaries(speaker_segments):
    summaries = []
    for speaker, text in speaker_segments.items():
        if not text:
            continue
        snippet = text.strip()
        if len(snippet) > 220:
            snippet = snippet[:220].rsplit(" ", 1)[0] + " ..."
        summaries.append({"speaker": speaker, "summary": snippet})
    return summaries


def summarize_speakers(speaker_segments, transcript_text):
    if not speaker_segments:
        return []

    trimmed = {speaker: _trim_for_prompt(text) for speaker, text in speaker_segments.items()}
    payload = json.dumps(trimmed, indent=2)
    user_input = (
        "Summarize what each speaker contributed in the meeting. "
        "Use the grouped transcript snippets below:\n\n"
        f"{payload}\n\n"
        f"Full transcript word count: {len(transcript_text.split())}"
    )

    raw = call_llm(SYSTEM_PROMPT_SPEAKER_BREAKDOWN, user_input)
    summaries = _parse_speaker_summary_response(raw)
    if summaries:
        return summaries

    return _fallback_speaker_summaries(speaker_segments)


def format_speaker_contributions(summaries):
    if not summaries:
        return ""

    lines = []
    for entry in summaries:
        speaker = entry.get("speaker")
        summary = entry.get("summary")
        if not speaker or not summary:
            continue
        lines.append(f"{speaker} — {summary}")

    return "\n".join(lines)


# ==========================================================
# PDF BUILDER (A2 MODE)
# ==========================================================
def build_pdf(folder, base_name, main_topic, summary_text, facts):
    pdf_path = os.path.join(folder, f"{base_name}_summary.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=10
    )

    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=16,
        spaceBefore=14,
        spaceAfter=8
    )

    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        alignment=TA_JUSTIFY,
        fontSize=11,
        leading=16
    )

    bullet = ParagraphStyle(
        "Bullet",
        parent=body,
        leftIndent=0.35 * inch,
        bulletIndent=0.2 * inch
    )

    story = []

    # ----- TITLE -----
    story.append(Paragraph(clean_title_spacing(main_topic), title_style))
    story.append(Spacer(1, 0.15 * inch))
    story.append(HRFlowable(width="100%", thickness=1))
    story.append(Spacer(1, 0.2 * inch))

    # ----- SPLIT SUMMARY -----
    lines = [l.strip() for l in summary_text.split("\n") if l.strip()]

    # Executive Overview paragraph
    exec_index = lines.index("Executive Overview") if "Executive Overview" in lines else 0
    exec_para = lines[exec_index + 1] if exec_index + 1 < len(lines) else ""

    story.append(Paragraph("Executive Overview", h2))
    story.append(Paragraph(f"<b>{exec_para}</b>", body))
    story.append(Spacer(1, 0.2 * inch))

    # Remaining sections parsed manually
    sections = [
        "Main Discussion Points",
        "Decisions Taken",
        "Action Items",
        "Unresolved Questions",
        "Speaker Contributions"
    ]

    # Find where the sections start to skip the overview
    start_index = -1
    for idx, line in enumerate(lines):
        if line in sections:
            start_index = idx
            break

    # ----- FOOTER -----
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(inch, 0.5 * inch,
                          "Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        canvas.drawRightString(A4[0] - inch, 0.5 * inch, f"Page {doc.page}")
        canvas.restoreState()

    if start_index == -1:  # No sections found
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        return pdf_path

    # Start the loop AT the first section
    i = start_index
    while i < len(lines):
        line = lines[i]

        if line in sections:
            # It's a heading
            story.append(Paragraph(line, h2))
            i += 1
            continue

        # If it's not a heading, it's a bullet point
        story.append(Paragraph("• " + line.strip("()"), bullet))
        i += 1

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return pdf_path


# ==========================================================
# SAVE OUTPUTS
# ==========================================================
def sanitize(o):
    if isinstance(o, dict):
        return {k: sanitize(v) for k, v in o.items()}
    if isinstance(o, list):
        return [sanitize(v) for v in o]
    if callable(o):
        return str(o)
    return o


def save_outputs(transcript, file_path, summary, facts, speaker_summaries):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.splitext(os.path.basename(file_path))[0]
    folder = os.path.join(OUTPUT_DIR, f"{base}_{timestamp}")
    os.makedirs(folder, exist_ok=True)

    # transcript
    txt_path = os.path.join(folder, "transcript.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(transcript.text)

    # json (summary + facts persisted for future reference)
    json_path = os.path.join(folder, "data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "transcript": transcript.text,
            "summary": summary,
            "facts": sanitize(facts),
            "speaker_summaries": speaker_summaries or []
        }, f, indent=2)

    print(f"✅ Outputs saved to: {folder}")

    # Return summary text instead of pdf path — PDF is now generated on-demand by frontend
    return txt_path, summary, json_path, folder, facts, speaker_summaries or []


# ==========================================================
# PROCESS FILE (USED BY FASTAPI)
# ==========================================================
def process_file(path):
    ext = os.path.splitext(path)[1].lower()
    temp_audio = None

    try:
        if ext in [".mp4", ".mov", ".avi", ".mkv"]:
            print("🎬 Extracting audio...")
            temp_audio = os.path.join(UPLOAD_DIR, f"temp_{datetime.now().timestamp()}.mp3")
            with VideoFileClip(path) as v:
                if not v.audio:
                    raise Exception("No audio track in video.")
                v.audio.write_audiofile(temp_audio, logger=None)
            ai_input = temp_audio
        else:
            ai_input = path

        transcript = transcribe_with_ai(ai_input)
        transcript_text = transcript.text

        facts = extract_facts(transcript_text)
        speaker_summaries = []

        # Dynamic prompt: longer overview for long transcripts
        word_count = len(transcript_text.split())
        LONG_TRANSCRIPT_THRESHOLD_WORDS = 3000

        if word_count > LONG_TRANSCRIPT_THRESHOLD_WORDS:
            overview_instruction = "(8–15 lines of clear prose, in one or two paragraphs)"
            print(f"📝 Long transcript detected ({word_count} words). Requesting detailed overview.")
        else:
            overview_instruction = "(3–4 lines of clear prose)"
            print(f"📝 Short transcript detected ({word_count} words). Requesting standard overview.")

        dynamic_summary_prompt = SYSTEM_PROMPT_SUMMARY.replace(
            "(3–4 lines of clear prose)",
            overview_instruction
        )

        summary_raw = call_llm(dynamic_summary_prompt, transcript_text)
        summary_clean = clean_summary(summary_raw)

        if speaker_summaries:
            speaker_section = format_speaker_contributions(speaker_summaries)
            if speaker_section:
                summary_clean = (
                    f"{summary_clean}\n\nSpeaker Contributions\n{speaker_section}"
                )

        topic = extract_topic(transcript_text)
        if isinstance(facts, dict):
            facts["meeting_topic"] = topic

        return save_outputs(transcript, path, summary_clean, facts, speaker_summaries)


    finally:
        if temp_audio and os.path.exists(temp_audio):
            os.remove(temp_audio)

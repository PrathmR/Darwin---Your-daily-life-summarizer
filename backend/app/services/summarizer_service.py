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

# Increase the SDK-wide HTTP timeout so large file uploads don't time out.
# The default is 30 s which is too short for big audio/video files.
aai.settings.http_timeout = 300.0  # 5 minutes

GEMINI_API_KEY_PRIMARY = os.getenv("GEMINI_API_KEY_PRIMARY")
GEMINI_API_KEY_FALLBACK = os.getenv("GEMINI_API_KEY_FALLBACK")

if not GEMINI_API_KEY_PRIMARY:
    raise SystemExit("❌ Missing GEMINI_API_KEY_PRIMARY")

# ==========================================================
# GEMINI MODEL
# ==========================================================
GEMINI_MODEL = "gemini-2.5-flash"
LONG_TRANSCRIPT_THRESHOLD_WORDS = 3000

# ==========================================================
# FORMAT TEMPLATES
# ==========================================================
FORMAT_TEMPLATES = {
    "default": {
        "description": "Executive Overview\n(3–4 lines of clear prose)\n\nMain Discussion Points\n(point 1)\n(point 2)\n(point 3)\n\nDecisions Taken\n(decision 1)\n\nAction Items\n(person — task)\n(person — task)\n\nUnresolved Questions\n(question 1)",
        "headings": ["Executive Overview", "Main Discussion Points", "Decisions Taken", "Action Items", "Unresolved Questions", "Speaker Contributions"]
    },
    "standup": {
        "description": "Daily Stand-Up Report\n\nTeam Members\n(member 1)\n(member 2)\n\nYesterday's Progress\n(Member A — task)\n(Member B — task)\n\nToday's Plan\n(Member A — task)\n(Member B — task)\n\nBlockers\n(blocker 1)\n\nSprint Progress Summary\n(component — status)",
        "headings": ["Daily Stand-Up Report", "Team Members", "Yesterday's Progress", "Today's Plan", "Blockers", "Sprint Progress Summary", "Speaker Contributions"]
    },
    "project_sync": {
        "description": "Project Status Report\n\nProject Name\n(name)\n\nMeeting Date\n(date)\n\nProject Updates\n(update 1)\n\nMilestones Achieved\n(milestone 1)\n\nPending Tasks\n(task 1)\n\nAssigned Responsibilities\n(person — responsibility)\n\nDeadlines\n(deadline 1)\n\nRisks / Challenges\n(risk 1)",
        "headings": ["Project Status Report", "Project Name", "Meeting Date", "Project Updates", "Milestones Achieved", "Pending Tasks", "Assigned Responsibilities", "Deadlines", "Risks / Challenges", "Speaker Contributions"]
    },
    "clinical": {
        "description": "Session Metadata\n(patient ID, clinician name, date, time, duration)\n\nAI Session Summary\n(concise overview of key themes and outcomes)\n\nSubjective (S)\n(patient-reported symptoms, feelings, experiences)\n\nObjective (O)\n(clinician-observed behaviors, physical signs)\n\nAssessment (A)\n(professional evaluation based on S and O)\n\nPlan (P)\n(recommended treatment plan, therapy strategies, follow-up actions)\n\nMedications\n(details of prescribed medications, dosage adjustments)\n\nDiagnoses (DSM/ICD)\n(clinical diagnosis coded)\n\nSafety & Risk Management\n(evaluation of potential risks, self-harm, etc.)\n\nNext Appointment\n(scheduled follow-up session timeline)\n\nAudit Trail\n(record of note creation/editing)",
        "headings": ["Session Metadata", "AI Session Summary", "Subjective (S)", "Objective (O)", "Assessment (A)", "Plan (P)", "Medications", "Diagnoses (DSM/ICD)", "Safety & Risk Management", "Next Appointment", "Audit Trail", "Speaker Contributions"]
    },
    "retrospective": {
        "description": "Sprint Retrospective Report\n\nSprint Number\n(number)\n\nTeam Members\n(member 1)\n\nWhat Went Well\n(item 1)\n\nWhat Didn't Go Well\n(item 1)\n\nLessons Learned\n(item 1)\n\nImprovement Actions\n(item 1)\n\nNext Sprint Goals\n(item 1)",
        "headings": ["Sprint Retrospective Report", "Sprint Number", "Team Members", "What Went Well", "What Didn't Go Well", "Lessons Learned", "Improvement Actions", "Next Sprint Goals", "Speaker Contributions"]
    },
    "sales": {
        "description": "Client Meeting Summary\n\nClient Name\n(name)\n\nMeeting Date\n(date)\n\nClient Requirements\n(requirement 1)\n\nDiscussion Highlights\n(highlight 1)\n\nDecisions\n(decision 1)\n\nCommitments Made\n(commitment 1)\n\nFollow-Up Actions\n(team/person — action)",
        "headings": ["Client Meeting Summary", "Client Name", "Meeting Date", "Client Requirements", "Discussion Highlights", "Decisions", "Commitments Made", "Follow-Up Actions", "Speaker Contributions"]
    }
}

def get_system_prompt_summary(format_type: str) -> str:
    template = FORMAT_TEMPLATES.get(format_type, FORMAT_TEMPLATES["default"])
    return f"""
You are an expert meeting analyst.

Generate a plain text meeting summary with these exact sections:

{template["description"]}

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
def call_gemini(prompt_text, api_key, model_name=GEMINI_MODEL):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        response = model.generate_content(prompt_text)

        if not response or not response.text:
            return None

        return response.text.strip()

    except Exception as e:
        print(f"⚠️ Gemini failed ({api_key[-4:]}): {e}")
        return None


def call_llm(system_prompt, user_input, custom_api_key=None, model_preference=None):
    full_prompt = system_prompt + "\n\n" + user_input
    
    # 0. Custom Key
    if custom_api_key:
        print(f"🔑 Using custom API key and model: {model_preference}")
        out = call_gemini(full_prompt, custom_api_key, model_preference or GEMINI_MODEL)
        if out:
            return out
        else:
            print("❌ Custom API call failed, falling back to default keys.")

    # 1. Primary
    if GEMINI_API_KEY_PRIMARY:
        out = call_gemini(full_prompt, GEMINI_API_KEY_PRIMARY, GEMINI_MODEL)
        if out:
            return out

    # 2. Fallback
    if GEMINI_API_KEY_FALLBACK:
        out = call_gemini(full_prompt, GEMINI_API_KEY_FALLBACK, GEMINI_MODEL)
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
def extract_facts(text, custom_api_key=None, model_preference=None, meeting_role=None):
    role_instruction = get_role_instructions(meeting_role)["facts"]
    prompt = SYSTEM_PROMPT_FACTS + f"\n\nROLE CONTEXT: {role_instruction}"
    out = call_llm(prompt, text, custom_api_key, model_preference)
    if not out:
        return {}

    try:
        return json.loads(out)
    except:
        return {"raw": out}


# ==========================================================
# ROLE-BASED PROMPT INJECTIONS
# ==========================================================
def get_role_instructions(role: str) -> dict:
    default_role = {
        "summary": "Focus on the general meeting flow, key discussion points, and standard action items.",
        "facts": "Extract standard action items, decisions, and participants without any specific role bias."
    }
    
    if not role or role == "general":
        return default_role
    
    roles = {
        "project_manager": {
            "summary": "You are a Project Manager condensing this meeting. Emphasize project timelines, blockers, clear ownership of action items, and risks discussed.",
            "facts": "Focus heavily on extracting concrete deliverables, deadlines, and who is blocked by whom. Ignore minor technical tangents."
        },
        "software_pm": {
            "summary": "You are a Software PM / Scrum Master. Emphasize sprint progress, Jira ticket mentions, technical blockers, PR reviews, and feature requirements.",
            "facts": "Extract specific feature names, PR numbers, technical constraints, and developer assignments. Structure action items tightly around code/deployment tasks."
        },
        "researcher": {
            "summary": "You are a Researcher summarizing this discussion. Highlight hypotheses, methodologies, data points cited, and logical conclusions.",
            "facts": "Extract data points, citations, novel ideas, and questions that require further investigation."
        },
        "psychiatrist": {
            "summary": "You are a Psychiatrist or Therapist making clinical notes. Emphasize patient mood, reported symptoms, behavioral observations, and treatment plans.",
            "facts": "Extract prescribed medications, emotional state markers, side effects discussed, and the concrete plan for the next session."
        },
        "standup_conductor": {
            "summary": "You are running a Daily Standup. Quickly summarize what was accomplished yesterday, what is planned for today, and any blockers (the Three Questions).",
            "facts": "Extract ONLY what people did, what they will do, and what is blocking them. Keep it extremely brief."
        }
    }
    
    return roles.get(role, default_role)


# ==========================================================
# TOPIC EXTRACTION
# ==========================================================
def extract_topic(text, custom_api_key=None, model_preference=None):
    out = call_llm(SYSTEM_PROMPT_TOPIC, text, custom_api_key, model_preference)
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
def clean_summary(text, format_type="default"):
    if not text:
        return ""

    # Remove markdown symbols
    text = text.replace("*", "").replace("#", "")

    # Split text into lines, clean each line, then rejoin.
    lines = text.split('\n')
    cleaned_lines: list = []
    for line in lines:
        cleaned_line = re.sub(r'[ \t]+', ' ', line).strip()
        cleaned_lines.append(cleaned_line)

    # Re-assemble, filtering out any blank lines
    text = "\n".join(l for l in cleaned_lines if l)

    # Ensure headings are separated by newlines
    headings = FORMAT_TEMPLATES.get(format_type, FORMAT_TEMPLATES["default"])["headings"]
    for heading in headings:
        regex_heading = re.escape(heading)
        text = re.sub(rf"({regex_heading})", r"\n\1\n", text, flags=re.IGNORECASE)

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

    segments: dict = {}
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


def summarize_speakers(speaker_segments, transcript_text, custom_api_key=None, model_preference=None):
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

    raw = call_llm(SYSTEM_PROMPT_SPEAKER_BREAKDOWN, user_input, custom_api_key, model_preference)
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

    story: list = []

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
    start_index: int = -1
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
    for i in range(start_index, len(lines)):
        line = lines[i]

        if line in sections:
            # It's a heading
            story.append(Paragraph(line, h2))
            continue

        # If it's not a heading, it's a bullet point
        story.append(Paragraph("• " + line.strip("()"), bullet))

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
def process_file(path, calendar_context=None, progress_callback=None, custom_api_key=None, model_preference=None, meeting_role=None, summary_format="default"):
    ext = os.path.splitext(path)[1].lower()
    temp_audio = None

    class MockTranscript:
        def __init__(self, text, utterances=None):
            self.text = text
            self.utterances = utterances

    try:
        if ext == ".txt":
            print("📄 Text file detected. Skipping transcription...")
            if progress_callback: progress_callback("Reading text transcript...")
            with open(path, "r", encoding="utf-8") as f:
                transcript_text = f.read()
            transcript = MockTranscript(transcript_text)
        else:
            if ext in [".mp4", ".mov", ".avi", ".mkv"]:
                print("🎬 Extracting audio...")
                if progress_callback: progress_callback("Extracting audio from video...")
                temp_audio = os.path.join(UPLOAD_DIR, f"temp_{datetime.now().timestamp()}.mp3")
                with VideoFileClip(path) as v:
                    if not v.audio:
                        raise Exception("No audio track in video.")
                    v.audio.write_audiofile(temp_audio, logger=None)
                ai_input = temp_audio
            else:
                ai_input = path

            if progress_callback: progress_callback("Transcribing with AssemblyAI...")
            raw_transcript = transcribe_with_ai(ai_input)
            
            # Format transcript text with timestamps if utterances are available
            if hasattr(raw_transcript, 'utterances') and raw_transcript.utterances:
                formatted_lines = []
                for utt in raw_transcript.utterances:
                    seconds = utt.start // 1000
                    minutes = seconds // 60
                    rem_seconds = seconds % 60
                    timestamp_str = f"[{minutes:02d}:{rem_seconds:02d}]"
                    speaker = f"Speaker {utt.speaker}" if utt.speaker else "Unknown"
                    formatted_lines.append(f"{timestamp_str} {speaker}: {utt.text}")
                transcript_text = "\n".join(formatted_lines)
                transcript = MockTranscript(transcript_text, raw_transcript.utterances)
            else:
                transcript_text = raw_transcript.text
                transcript = MockTranscript(transcript_text, None)

        # Inject Context If Available
        context_prefix = ""
        if calendar_context:
            context_prefix = f"=== GOOGLE CALENDAR MEETING CONTEXT ===\n{calendar_context}\n=======================================\n\n"
        
        enriched_text = context_prefix + transcript_text

        if progress_callback: progress_callback("Extracting meeting facts and insights...")
        facts = extract_facts(enriched_text, custom_api_key, model_preference, meeting_role)
        
        # Speaker Summaries
        if progress_callback: progress_callback("Analyzing speaker contributions...")
        speaker_segments = extract_speaker_segments(transcript)
        speaker_summaries = summarize_speakers(speaker_segments, transcript_text, custom_api_key, model_preference)

        dynamic_summary_prompt = get_system_prompt_summary(summary_format)
        word_count = len(enriched_text.split())

        if word_count > LONG_TRANSCRIPT_THRESHOLD_WORDS:
            dynamic_summary_prompt += "\n\nNOTE: Because this is a long transcript, please provide a highly detailed, comprehensive summary."

        role_instruction = get_role_instructions(meeting_role)["summary"]
        dynamic_summary_prompt += f"\n\nROLE CONTEXT: {role_instruction}"

        if progress_callback: progress_callback("Generating structured summary with Gemini...")
        summary_raw = call_llm(dynamic_summary_prompt, enriched_text, custom_api_key, model_preference)
        summary_clean = clean_summary(summary_raw, summary_format)

        if speaker_summaries:
            speaker_section = format_speaker_contributions(speaker_summaries)
            if speaker_section:
                summary_clean = (
                    f"{summary_clean}\n\nSpeaker Contributions\n{speaker_section}"
                )

        topic = extract_topic(enriched_text, custom_api_key, model_preference)
        if isinstance(facts, dict):
            facts["meeting_topic"] = topic

        if progress_callback: progress_callback("Saving outputs...")
        return save_outputs(transcript, path, summary_clean, facts, speaker_summaries)


    finally:
        if temp_audio and os.path.exists(temp_audio):
            os.remove(temp_audio)

# ==========================================================
# PROCESS TEXT ONLY (FOR LIVE RECORDINGS)
# ==========================================================
def process_text(transcript_text: str, calendar_context=None, progress_callback=None, custom_api_key=None, model_preference=None, meeting_role=None, summary_format="default"):
    # Inject Context If Available
    context_prefix = ""
    if calendar_context:
        context_prefix = f"=== GOOGLE CALENDAR MEETING CONTEXT ===\n{calendar_context}\n=======================================\n\n"
    
    enriched_text = context_prefix + transcript_text

    if progress_callback: progress_callback("Extracting meeting facts and insights...")
    facts = extract_facts(enriched_text, custom_api_key, model_preference, meeting_role)
    speaker_summaries = []

    dynamic_summary_prompt = get_system_prompt_summary(summary_format)
    word_count = len(enriched_text.split())

    if word_count > LONG_TRANSCRIPT_THRESHOLD_WORDS:
        dynamic_summary_prompt += "\n\nNOTE: Because this is a long transcript, please provide a highly detailed, comprehensive summary."

    role_instruction = get_role_instructions(meeting_role)["summary"]
    dynamic_summary_prompt += f"\n\nROLE CONTEXT: {role_instruction}"

    if progress_callback: progress_callback("Generating structured summary with Gemini...")
    summary_raw = call_llm(dynamic_summary_prompt, enriched_text, custom_api_key, model_preference)
    summary_clean = clean_summary(summary_raw, summary_format)

    topic = extract_topic(enriched_text, custom_api_key, model_preference)
    if isinstance(facts, dict):
        facts["meeting_topic"] = topic

    class DummyTranscript:
        text = transcript_text
        
    fake_path = os.path.join(UPLOAD_DIR, "live_recording.txt")

    if progress_callback: progress_callback("Saving outputs...")
    return save_outputs(DummyTranscript(), fake_path, summary_clean, facts, speaker_summaries)

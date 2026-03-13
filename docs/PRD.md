# 📋 Darwin — Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** March 13, 2026  
**Author:** Prathmesh R.  
**Status:** Active

---

## 1. Executive Summary

**Darwin** is a full-stack, AI-powered meeting intelligence platform that transforms meeting recordings into structured, actionable summaries. It automates the entire post-meeting workflow — from transcription and speaker identification to insight extraction, task assignment, and professional report generation — enabling teams to focus on collaboration while the platform handles documentation.

---

## 2. Problem Statement

### 2.1 The Challenge

In today's remote and hybrid work environments, meetings are the primary communication channel. However, critical information is routinely lost:

- **Information Overload:** Professionals attend 5–8 meetings daily, making comprehensive recall impossible.
- **Unreliable Documentation:** Manual note-taking is subjective, incomplete, and biased toward the note-taker's perspective.
- **Unwatched Recordings:** Over 70% of recorded meetings are never revisited due to time constraints.
- **No Structured Output:** Even when meetings are summarized manually, the output lacks consistency — decisions, action items, and accountability are scattered or entirely lost.
- **Accountability Gaps:** Without clear, automated task attribution, follow-ups are missed and ownership becomes ambiguous.

### 2.2 Opportunity

Darwin addresses these pain points by automating the entire meeting intelligence pipeline, transforming unstructured audio into structured, actionable data — reducing post-meeting administrative burden by an estimated 80%.

---

## 3. Target Users & Personas

### Persona 1: The Project Manager (Primary)
- **Name:** Ayesha, 28, PM at a mid-size tech company
- **Pain Point:** Spends 45+ minutes after each meeting writing summaries and tracking action items
- **Goal:** Automated post-meeting reports with clear task ownership and deadlines
- **Darwin Value:** Upload recording → Get actionable summary + auto-emailed tasks in minutes

### Persona 2: The Remote Team Lead
- **Name:** Rahul, 32, Engineering Lead managing a distributed team
- **Pain Point:** Team members in different time zones miss meeting context
- **Goal:** Async meeting digests that capture decisions and who said what
- **Darwin Value:** Speaker-attributed summaries with key decision tracking

### Persona 3: The Student / Researcher
- **Name:** Priya, 22, Graduate student
- **Pain Point:** Long lecture recordings that take hours to manually review
- **Goal:** Concise summaries of hour-long lectures with key quotes and topics
- **Darwin Value:** Upload lecture audio → Get structured notes with topic extraction

### Persona 4: The Executive
- **Name:** Vikram, 45, VP of Operations
- **Pain Point:** Needs quick meeting digests without watching full recordings
- **Goal:** Professional PDF reports that can be shared with stakeholders
- **Darwin Value:** Downloadable, branded PDF reports generated automatically

---

## 4. Product Vision & Goals

### 4.1 Vision Statement

> **"Every meeting deserves perfect recall."** — Darwin eliminates the trade-off between participating in a meeting and documenting it, using AI to deliver complete, structured, and actionable meeting intelligence.

### 4.2 Strategic Goals

| # | Goal | Success Metric |
|---|------|----------------|
| G1 | Reduce post-meeting documentation time | < 5 minutes from upload to complete summary |
| G2 | Ensure no action item is lost | 95%+ Action Item extraction accuracy |
| G3 | Enable async collaboration | Summaries accessible to all authenticated team members |
| G4 | Provide professional outputs | Downloadable PDF reports for stakeholders |
| G5 | Support real-time use cases | Live transcription with real-time summary UI |

---

## 5. Feature Specifications

### 5.1 Authentication & User Management

| Feature | Description | Priority |
|---------|-------------|----------|
| Email/Password Registration | Secure sign-up with Argon2 password hashing | P0 |
| Email Verification | SMTP-based tokenized email confirmation links | P0 |
| Google OAuth 2.0 | One-click sign-in via Google accounts | P0 |
| JWT Session Management | httpOnly cookie-based access + refresh tokens | P0 |
| Token Refresh | Seamless silent token renewal with versioned refresh tokens | P0 |
| Protected Routes | Auth-gated access to dashboard and summarizer | P0 |
| Profile Dropdown | User avatar and profile management in navigation | P1 |

---

### 5.2 Meeting Upload & Processing

| Feature | Description | Priority |
|---------|-------------|----------|
| File Upload | Accept audio/video files (MP3, WAV, MP4, MOV, AVI, MKV) | P0 |
| Audio Extraction | Automatic audio strip from video files via MoviePy | P0 |
| Speech-to-Text | AssemblyAI transcription with punctuation and formatting | P0 |
| Speaker Diarization | Identify and separate speakers (Speaker A, B, etc.) | P0 |
| Entity Detection | Detect names, organizations, and other entities | P1 |
| Auto-Highlights | Identify important phrases and keywords | P1 |

---

### 5.3 AI-Powered Intelligence Extraction

| Feature | Description | Priority |
|---------|-------------|----------|
| Meeting Topic Detection | Auto-detect meeting topic in 3–8 words | P0 |
| Structured Fact Extraction | Topics, participants, decisions, action items, issues, quotes | P0 |
| Executive Summary | Concise 3–15 line plain-text meeting overview | P0 |
| Action Item Extraction | Tasks with assignee names, emails, and deadlines | P0 |
| Speaker-by-Speaker Summary | Per-speaker contribution summaries | P0 |
| Dynamic Summary Length | Longer summaries for long meetings (>3000 words) | P1 |
| Dual-Key Gemini Fallback | Automatic failover to backup API key on rate limits | P1 |

---

### 5.4 Automated Task Management

| Feature | Description | Priority |
|---------|-------------|----------|
| Task Extraction | Parse action items from AI output into Task records | P0 |
| Email Detection | Regex-based extraction of assignee email addresses | P0 |
| Auto Email Dispatch | Automated SMTP task assignment emails to assignees | P0 |
| Task Status Tracking | Track task states: `pending` → `emailed` → `completed` | P1 |

---

### 5.5 Report Generation & Storage

| Feature | Description | Priority |
|---------|-------------|----------|
| PDF Report Generation | Professional, styled PDF via ReportLab (A4, headers, bullets) | P0 |
| Transcript File (.txt) | Raw timestamped transcript with speaker tags | P0 |
| Structured Data (.json) | Structured meeting data for programmatic access | P0 |
| Output Directory Management | Timestamped folders per meeting in `output_summaries/` | P0 |

---

### 5.6 Dashboard & User Experience

| Feature | Description | Priority |
|---------|-------------|----------|
| Summary Dashboard | List of all past summaries with timestamps | P0 |
| Summary Detail View | View full summary, facts, and speaker breakdown | P0 |
| Search & Sort | Search summaries by topic/filename | P1 |
| Landing Page | Feature overview with marketing content | P0 |
| Responsive Design | Desktop and mobile-friendly layouts | P0 |
| Toast Notifications | Real-time feedback on actions via Sonner | P1 |

---

### 5.7 Real-Time Live Processing

| Feature | Description | Priority |
|---------|-------------|----------|
| WebSocket Connection | Real-time bidirectional communication | P0 |
| Live Audio Recording | Capture system/browser tab audio in real-time | P0 |
| Real-Time Transcription | Stream audio for live speech-to-text | P0 |
| Progress Updates | WebSocket-pushed stage-by-stage progress messages | P1 |
| Live Summary Generation | Summarize live transcript on recording stop | P0 |

---

## 6. User Flows

### 6.1 Meeting Upload Flow

```
User logs in → Navigates to Create Game (Summarizer)
  → Uploads meeting file (audio/video)
  → System extracts audio (if video)
  → System transcribes with AssemblyAI (speaker diarization)
  → System extracts facts with Gemini AI
  → System generates summary
  → System sends task emails to detected assignees
  → System saves to database + generates PDF
  → User views results (summary, facts, speaker breakdown)
  → User downloads PDF report
```

### 6.2 Live Meeting Flow

```
User logs in → Navigates to Live Summarizer
  → Starts live audio capture (system audio / browser tab)
  → Real-time transcription displayed via WebSocket
  → User stops recording
  → System processes full transcript through Gemini pipeline
  → Summary displayed + saved to dashboard
```

### 6.3 Dashboard Flow

```
User logs in → Redirected to Dashboard
  → Views list of past summaries (sorted newest first)
  → Clicks a summary card
  → Views full summary text, extracted facts, speaker contributions
```

---

## 7. Output Specifications

### 7.1 AI-Extracted JSON Structure

```json
{
  "meeting_topic": "Project Alpha Launch Discussion",
  "topics": ["Timeline revision", "Budget allocation"],
  "participants": ["Alice", "Bob", "Carol"],
  "decisions": ["Launch delayed to Q3", "Budget increased by 10%"],
  "action_items": [
    {
      "assignee": "Alice (alice@company.com)",
      "task": "Update marketing materials",
      "deadline": "2026-03-20"
    }
  ],
  "issues_discussed": ["Server capacity limits"],
  "important_quotes": ["This is our most important release. - Alice"]
}
```

### 7.2 Summary Sections

| Section | Content |
|---------|---------|
| Executive Overview | 3–15 lines of concise prose |
| Main Discussion Points | Key topics covered |
| Decisions Taken | Agreements and conclusions |
| Action Items | Person → Task mappings |
| Unresolved Questions | Open items needing follow-up |
| Speaker Contributions | Per-speaker contribution summaries |

### 7.3 PDF Report

- **Format:** A4, 1-inch margins
- **Styling:** Custom heading styles, justified body text, bulleted lists
- **Footer:** Auto-generated timestamp + page number
- **Content:** Executive overview, discussion points, decisions, action items, unresolved questions

---

## 8. Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| **Performance** | < 5 min end-to-end for 60-min meeting recording |
| **Security** | Argon2 hashing, httpOnly JWT cookies, CORS allowlisting, server-side OAuth verification |
| **Availability** | Dual-key API strategy for Gemini (failover on rate limit) |
| **Scalability** | SQLite for dev; PostgreSQL-ready for production |
| **Compatibility** | Audio: MP3, WAV, M4A, FLAC. Video: MP4, MOV, AVI, MKV |
| **Data Retention** | All outputs (txt, json, pdf) persisted in `output_summaries/` + database |

---

## 9. Future Roadmap

| Phase | Feature | Description |
|-------|---------|-------------|
| **Phase 1** | Calendar Integration | Auto-process scheduled meeting recordings from Google Calendar |
| **Phase 2** | Task Management Integration | Push action items to Jira, Asana, or Trello |
| **Phase 3** | Emotion & Sentiment Detection | Analyze meeting tone to highlight critical or tense moments |
| **Phase 4** | Multi-Language Support | Extend transcription to non-English languages |
| **Phase 5** | Team Workspaces | Shared summary access across team members |
| **Phase 6** | Cloud Deployment | Deploy to AWS/GCP/Azure with PostgreSQL |
| **Phase 7** | Visual Modal Integration | OCR on screen-shares, slide understanding |

---

## 10. Success Metrics

| Metric | Target |
|--------|--------|
| Upload-to-summary latency | < 5 minutes for 60-min recordings |
| Action item extraction accuracy | > 90% |
| PDF generation success rate | 100% |
| User retention (monthly) | > 60% |
| Task email delivery rate | > 95% |

---

## 11. Assumptions & Constraints

### Assumptions
- Users have access to meeting recordings (audio or video files)
- Internet connectivity available for AssemblyAI and Gemini API calls
- Gmail SMTP is available for task email dispatch

### Constraints
- AssemblyAI free-tier usage limits apply
- Gemini API rate limits mitigated via dual-key strategy
- SQLite is single-writer (limits concurrent processing in production)

---

## 12. Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| AssemblyAI API | External | Speech-to-text transcription with diarization |
| Google Gemini API | External | LLM-based intelligence extraction and summarization |
| Google OAuth 2.0 | External | Social authentication |
| Gmail SMTP | External | Task assignment email delivery |

---

*End of PRD*

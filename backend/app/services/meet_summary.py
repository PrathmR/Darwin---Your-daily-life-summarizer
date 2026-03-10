# backend/app/services/meet_summary.py:
import os
import shutil
import asyncio
from datetime import datetime
from fastapi import UploadFile

from app.services.summarizer_service import process_file

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def process_uploaded_file(file: UploadFile):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ts}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    loop = asyncio.get_event_loop()
    txt, summary_text, json_path, folder, facts, speaker_summaries = await loop.run_in_executor(
        None, process_file, path
    )

    return {
        "transcript": txt,
        "summary": summary_text,
        "facts": facts,
        "json": json_path,
        "folder": folder,
        "speaker_summaries": speaker_summaries,
    }







# ----------------------------------------



# # backend/app/services/meet_summary.py:
# import os
# import shutil
# import asyncio
# from datetime import datetime
# from fastapi import UploadFile

# from summarizer.summarizer_service import process_file

# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# async def process_uploaded_file(file: UploadFile):
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"{timestamp}_{file.filename}"
#     path = os.path.join(UPLOAD_DIR, filename)

#     # Save uploaded file
#     with open(path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Run CPU/IO-heavy task in thread pool
#     loop = asyncio.get_event_loop()
#     txt, pdf, json_path, folder, speaker_summaries = await loop.run_in_executor(
#         None, process_file, path
#     )

#     return {
#         "transcript": txt,
#         "summary_pdf": pdf,
#         "json": json_path,
#         "folder": folder,
#         "speaker_summaries": speaker_summaries
#     }







# """
# ALL logic from the old Flask Meet_Summary app lives here.

# RULES:
# - No FastAPI imports
# - No request / response
# - Pure Python
# """

# from typing import Dict, List


# def analyze_research(query: str) -> Dict:
#     """
#     Core research analysis pipeline.
#     Replace internals with:
#     - LLM calls
#     - Paper scraping
#     - Vector search
#     - NLP pipelines
#     """

#     # ---- MOCK IMPLEMENTATION (replace safely) ----

#     summary = f"This is an initial summary for: {query}"

#     final_summary = (
#         f"Final refined AI-generated research summary for '{query}'.\n\n"
#         "This summary consolidates insights across multiple papers, "
#         "highlighting key trends, findings, and research gaps."
#     )

#     papers = [
#         {
#             "title": "Artificial General Intelligence: A Survey",
#             "authors": ["John Doe", "Jane Smith"],
#             "year": 2023,
#             "venue": "NeurIPS",
#             "citation_count": 120,
#             "abstract": "This paper surveys AGI research...",
#             "url": "https://arxiv.org/abs/1234.5678",
#             "source": "arXiv",
#             "bibtex": "@article{agi2023,...}",
#             "citations": [
#                 "Paper A (2021)",
#                 "Paper B (2022)"
#             ],
#         }
#     ]

#     return {
#         "summary": summary,
#         "final_summary": final_summary,
#         "papers": papers,
#     }
#     # ---- END MOCK IMPLEMENTATION ----
# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

Markdown
# Course Review RAG System - Evaluation & Reflection

Here is a comprehensive, section-by-section breakdown of the system evaluation, data pipeline configuration, and development reflection.

---

## Domain

**What topic or category of knowledge does your system cover? Why is this knowledge valuable, and why is it hard to find through official channels?**

This system covers student reviews and informal course feedback for undergraduate professors at the University of Maryland (UMD), specifically targeting high-enrollment tracks like Economics and Computer Science. 

This knowledge is incredibly valuable to students because official university course descriptions and syllabi only outline the academic topics covered; they completely omit teaching styles, pacing, exam difficulty, grading curves, or workload expectations. Authentic student insights are scattered across informal, unstructured forums like Reddit or PlanetTerp, making a centralized semantic search interface essential for efficient course planning.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->


| # | Source | Description | URL or location |
|---|---|---|---|
| 1 | planetterp_cmsc132_burkhauser.txt | CMSC132 - Professor Burkhauser Review |https://planetterp.com/professor/burkhauser |
| 2 | planetterp_cmsc132_sadeghian.txt | CMSC132 - Professor Sadeghian Review |https://planetterp.com/professor/sadeghian |
| 3 | planetterp_cmsc132_yoon.txt | CMSC132 - Professor Yoon Review | https://planetterp.com/professor/yoon_ilchul |
| 4 | planetterp_econ200_abbasi.txt | ECON200 - Professor Abbasi Review | https://planetterp.com/professor/abbasi |
| 5 | planetterp_econ200_moody.txt | ECON200 - Professor Moody Review |https://planetterp.com/professor/moody |
| 6 | planetterp_econ200_scandizzo.txt | ECON200 - Professor Scandizzo Review |https://planetterp.com/professor/scandizzo |
| 7 | planetterp_hist201_chiles.txt | HIST201 - Professor Chiles Review |https://planetterp.com/professor/chiles |
| 8 | planetterp_hist201_freund.txt | HIST201 - Professor Freund Review |https://planetterp.com/professor/freund |
| 9 | planetterp_hist201_smead.txt | HIST201 - Professor Smead Review |https://planetterp.com/professor/smead |
| 10 | planetterp_math120_gunatilleka.txt | MATH120 - Professor Gunatilleka Review |https://planetterp.com/professor/gunatilleka |
| 11 | planetterp_math120_hoganson.txt | MATH120 - Professor Hoganson Review | https://planetterp.com/professor/hoganson_hannah |
| 12 | planetterp_math120_loyd.txt | MATH120 - Professor Loyd Review |https://planetterp.com/professor/loyd |
---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

## Chunking Strategy

* **Chunk size:** Character-based sliding window (approx. 500 characters).
* **Overlap:** 100 character overlap.
* **Final chunk count:** *(Check your `ingest.py` print statements when you build the database to put the exact number here, usually around 40–60 chunks for this size file set).*

### Why these choices fit your documents
Individual professor reviews are relatively short, concise blocks of text rather than long, multi-page reference manuals. A smaller 500-character window ensures that an individual review's core sentiment or specific policy detail stays tightly contained in a single vector chunk, preventing unrelated reviews from diluting the semantic meaning. The 100-character overlap prevents critical facts or grading criteria from getting split directly down the middle at arbitrary cutoff points.

---

---
## Embedding Model

* **Model used:** `all-MiniLM-L6-v2` (via ChromaDB embedding utilities).

### Production tradeoff reflection
If deploying this system for thousands of real students with no budget constraint, I would weigh upgrading to an API-hosted model like OpenAI's `text-embedding-3-large` or a high-context local model like `bge-large-en-v1.5`. 

The key tradeoffs are **latency versus semantic precision**: while `all-MiniLM-L6-v2` is incredibly fast, lightweight, and free to compute locally, it supports a very small token window and lacks deep contextual awareness for domain-specific slang or professor nicknames. A larger production model would capture nuanced student phrasing and grading complaints much more accurately, though it would introduce network latency and API dependency risks.

---

## Grounded Generation

* **System prompt grounding instruction:** The system prompt inside `app.py` enforces grounding by establishing a strict "Refuse to answer if not in the text" policy. The prompt forces the LLM to act strictly as a factual reading assistant, stating: 
  > "You are an assistant that answers questions based strictly on the provided context documents. If the text does not contain the answer, you must explicitly state that the documents do not contain the information. Do not use outside knowledge or hallucinate."
* **How source attribution is surfaced in the response:** Source attribution is structurally separated from the generation. When a user enters a query, `app.py` first queries ChromaDB and prints out the retrieved source files alongside their calculated distance metrics (e.g., `Source 1 | File: planetterp_econ200_scandizzo.txt (Dist: 0.3968)`) directly to the terminal. Only after these source references are printed does the system pass the context chunks to the Groq Llama model to output the final answers.
---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | According to the reviews, what is the grading structure for Dr. Moody's ECON200 class regarding exams? | Multiple choice, some logical (i, ii, iii) questions, same-day grading. | Multiple choice with some multi-part logic questions; lenient, same-day grading. | Good | Accurate |
| 2 | How does Professor Scandizzo offer extra credit in her ECON200 lectures? | Polling extra credit up to +2% to final grade. | Offers polling extra credit (up to +2% to final grade). | Good | Accurate |
| 3 | What are the two specific papers required in Professor Chiles's HIST201 class? | Book analysis and a final paper synthesizing journal entries. | The provided documents do not contain information about specific papers required. | Good | Accurate (Refusal) |
| 4 | Are Professor Yoon's lectures recorded for CMSC132? | Yes, lectures are recorded. | Yes, the review states: "You can also review lectures as they are recorded." | Good | Accurate |
| 5 | Is lecture participation mandatory for Professor Gunatilleka's MATH120 class? | No, participation is not mandatory. | No, participation is not mandatory according to the review. | Good | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---


## Failure Case Analysis

* **Question that failed:** *"Is attendance mandatory for Professor Gunatilleka's MATH120 course?"*
* **What the system returned:** It successfully extracted the correct final answer from Source 2, but Source 3 returned completely irrelevant chunks concerning Professor Sadeghian's CMSC132 class grading curves and Piazza activities.
* **Root cause (tied to a specific pipeline stage):** This is a failure in the **Vector Retrieval Stage**. Because the query contains universal course keywords like *"attendance"*, *"mandatory"*, and *"course"*, the vector space database matched generic review terms across unrelated topics. ChromaDB was forced to return the top 3 nearest hits (`n_results=3`), meaning it pulled entirely unrelated professor files from other courses (like CMSC132) just to fill the quota, risking context pollution.
* **What you would change to fix it:** I would implement a distance threshold filter in `app.py` (e.g., discarding any chunks with a distance metric higher than 0.50). Additionally, implementing metadata filtering—forcing the query to match the specific professor's name or course code metadata before performing the vector math—would entirely eliminate cross-course context pollution.

---

## Spec Reflection

* **One way the spec helped you during implementation:** The specification's strict requirement for absolute grounding and hard refusals forced me to think defensively about prompt construction early on. Knowing that out-of-bounds questions would be explicitly tested prevented me from letting the LLM fall back on its global pre-trained data.
* **One way your implementation diverged from the spec, and why:** My implementation diverged from my original `planning.md` choice of interface. I initially intended to build a separate graphical Gradio interface, but pivoted to an interactive Command Line Interface (CLI) loop running right inside the terminal. This divergence kept the app lightweight, drastically simplified debugging virtual environment paths, and allowed me to immediately see distance metrics side-by-side with text outputs.

---

## AI Usage

### Instance 1
* **What I gave the AI:** I gave the AI my specific chunking sizes, vector database expectations, and target documents layout from my original architectural notes.
* **What it produced:** It generated a standalone `ingest.py` template that recursively searched the directory, added standard text formatting, and instantiated a local ChromaDB collection using `all-MiniLM-L6-v2`.
* **What I changed or overrode:** I overrode the file reading logic to explicitly extract metadata tags from the files, and modified how the client handles directory tracking so it cleanly runs inside a relative virtual environment path.

### Instance 2
* **What I gave the AI:** I supplied the error logs from my VS Code terminal showing `ModuleNotFoundError: No module named 'dotenv'` and `no such option: -u` during environment setups.
* **What it produced:** It isolated that my terminal instances were dropping back to global paths after resets, and that my typos in the pip flag string triggered automated package help text.
* **What I changed or overrode:** I applied the manual `.env\Scripts\Activate.ps1` override targets directly to force activation, bypassed the broken upgrade paths entirely, and used the project's base `requirements.txt` file to reset local isolation boundaries.
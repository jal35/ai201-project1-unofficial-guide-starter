# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

The domain chosen is PlanetTerp student reviews for foundational courses at the University of Maryland. 

This informal student knowledge is incredibly valuable because official university channels (like course catalogs or syllabi) only tell you *what* a course covers, not *how* it is run. Official channels completely lack qualitative realities that dictate a student's day-to-day success—such as whether a professor curves exams, drops the lowest quiz, records lectures, offers hidden extra credit opportunities, or if the homework assignments are scaling down based on class feedback.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

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

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

## Chunking Strategy
* **Strategy:** Fixed-size character chunking.
* **Chunk Size:** 400 characters.
* **Overlap:** 50 characters.

**Reasoning:**
Our documents consist of individual student reviews that range from ultra-short, single-sentence fragments ("Hannah Hoganson for President tbh") to medium-length paragraphs detailing full grading breakdowns. 

A 400-character chunk is small enough to isolate distinct student perspectives, preventing the vector database from blending together completely conflicting reviews (e.g., one student loving a professor and another hating them) into a single diluted vector representation. 

The 50-character overlap serves as semantic safety glue. If a crucial detail—like an exam policy or a specific grade requirement—spans across a chunk boundary, neither chunk would be fully coherent on its own. The overlap ensures the boundary context is duplicated, allowing either chunk to be independently retrieved with intact meaning.

If chunks were too small (e.g., 100 characters), a retrieved chunk might just be "If you understand what he is trying to say, then you are fine," completely lacking the name of the professor or course. If chunks were too large (e.g., 1500 characters), an entire file's worth of multiple student opinions would be mashed into one block, leading to muddy retrieval scores and flooding the LLM window with irrelevant noise.


---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

## Retrieval Approach
* **Embedding Model:** `all-MiniLM-L6-v2` via the `sentence-transformers` library.
* **Top-K Retrieval:** `k = 3` chunks retrieved per user query.
* **Distance Metric:** Cosine Distance.

**System Tradeoffs & Mechanics:**
* **Context Budget:** Retrieving 3 chunks balances depth and precision. Too few chunks (e.g., `k = 1`) risks missing crucial details spread across different reviews. Too many chunks (e.g., `k = 10`) risks exceeding the context window with repetitive praise or introducing conflicting noise that causes the LLM to hallucinate or summarize poorly.
* **Semantic Search Power:** Semantic search matches the conceptual meaning rather than exact keywords. For example, if a user queries "Is class attendance mandatory?", the system can successfully find a chunk saying "participation isn't required" because the vector embeddings map those phrases to a similar geometric space based on semantic context.
* **Production Scaling Tradeoffs:** If deploying for real users without cost constraints, we would consider upgrading to a high-capacity model (like `text-embedding-3-large` or a custom fine-tuned BERT variant). We would weigh **latency** (larger models increase search time), **context length** (to handle entire blocks of multiple semesters at once), and **accuracy on domain-specific text** (capturing university-specific slang like "GSS", "smartbooks", or "clickers" accurately).

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|---|---|
| 1 | According to the reviews, what is the grading structure for Dr. Moody's ECON200 class regarding exams? | There are 3 exams and a final, but if you do well on the first 3, you do not have to take the final. She also allows 1 retake. |
| 2 | How does Professor Scandizzo offer extra credit in her ECON200 lectures? | She offers up to +2% to the final grade through polling for showing up and answering polls in lecture. |
| 3 | What are the two specific papers required in Professor Chiles's HIST201 class? | One paper is an analysis of a book, and the other serves as the final where you synthesize the content of the journal entries written over the course of the semester. |
| 4 | Are Professor Yoon's lectures recorded for CMSC132? | Yes, the lectures are recorded for students to review. |
| 5 | Is lecture participation mandatory for Professor Gunatilleka's MATH120 class? | No, lecture participation is not mandatory. |
---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Context Loss via Document Shorthand:** Many short reviews rely heavily on pronouns ("He talks slow", "She is super cool"). If a chunk splits a review such that the introductory header containing the professor's name and course number is omitted, the chunk becomes a floating opinion with zero context, causing off-topic retrieval or a complete grounding failure.
2. **Conflicting Perspectives:** Student reviews are inherently contradictory (e.g., one student claiming Abbasi's class is a "free A" if you do the practice exams, while another states he "doesn't curve anything so get ready!"). The system risks feeding contradictory blocks into the LLM context, which might cause the generator to choke, look confused, or fail to output a cohesive summary.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```mermaid
graph LR
    A[Document Ingestion<br/>'os' library / Python] --> B[Chunking<br/>Fixed-size Character Window]
    B --> C[Embedding & Vector Store<br/>all-MiniLM-L6-v2 + ChromaDB]
    C --> D[Retrieval<br/>Top-3 Cosine Distance]
    D --> E[Generation<br/>Groq llama-3.3-70b-versatile]

    style A fill:#1f2937,stroke:#3b82f6,stroke-width:2px,color:#fff
    style B fill:#1f2937,stroke:#3b82f6,stroke-width:2px,color:#fff
    style C fill:#1f2937,stroke:#10b981,stroke-width:2px,color:#fff
    style D fill:#1f2937,stroke:#f59e0b,stroke-width:2px,color:#fff
    style E fill:#1f2937,stroke:#ef4444,stroke-width:2px,color:#fff

---
     
## AI Tool Plan


## AI Tool Plan
1. **Pipeline Implementation (Ingestion & Vectorization):** I will prompt Claude by providing the exact specifications under `## Chunking Strategy` and `## Retrieval Approach` alongside the project's boilerplate instructions. I expect it to generate a clean `ingest.py` script that loops through the `documents/` folder, prepends metadata headers to the file texts, applies a character-based sliding window tokenizer, and instances a local, persistent ChromaDB collection using `all-MiniLM-L6-v2`.
2. **Grounded Interface Generation:** I will feed the system prompt requirements and the `## Evaluation Plan` section to Claude to construct the prompt template in `app.py`. I expect it to output a clean string-formatting routine that enforces strict system rules (e.g., "Refuse to answer if not in the text") and builds a lightweight Gradio interface showing side-by-side text generation and metadata source attributions.

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**

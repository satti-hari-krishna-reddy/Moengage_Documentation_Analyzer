# AI-Powered Documentation Improvement Agent

## Table of Contents

* [Overview](#overview)
* [Setup Instructions](#setup-instructions)
* [Assumptions](#assumptions)
* [Architecture](#architecture)
* [Design Decisions & Strategy](#design-decisions--strategy)

  * [Agent 1 - Analysis Agent](#agent-1---analysis-agent)
  * [Agent 2 - Revision Agent](#agent-2---revision-agent)
* [Challenges Faced](#challenges-faced)
* [Future Improvements](#future-improvements)

---

## Overview

This project was built as part of MoEngage's Tech Internship Assessment. The objective was to build one or more AI-powered agents that can analyze and revise public documentation articles from [help.moengage.com](https://help.moengage.com/hc/en-us/articles/...).

I developed:

* **Agent 1:** A documentation analysis agent that generates a structured list of actionable improvements.
* **Agent 2:** A revision agent that attempts to apply those suggestions automatically.

---

## Setup Instructions

1. **Clone the repository:**

```bash
git clone https://github.com/satti-hari-krishna-reddy/Moengage_Documentation_Analyzer
cd Moengage_Documentation_Analyzer
```

2. **Create and activate virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. Make sure these packages are installed on your system before running the app (especially needed for headless browser functionality). If any of them are already installed, you can ignore them:

```bash
sudo apt-get install libwoff1 libevent-2.1-7t64 libgstreamer-plugins-bad1.0-0 libharfbuzz-icu0 libenchant-2-2 libhyphen0 libmanette-0.2-0
```


5. **Set the Gemini API Key:**
   Gemini Api key as an env variable:

```
export GEMINI_API_KEY=your_api_key_here
```

6. **Run Agent 1 (Analyzer):**

```bash
python main.py
```

This will generate `analysis_report.json` and `scraped_text.txt`.

7. **Run Agent 2 (Revision - Optional Bonus Task):**

```bash
python agent-2.py
```

This will generate a `revised_document.txt` using suggestions from Agent 1.

---

## Assumptions

* I assume the target audience is marketers with limited technical background.
* Due to bot protection on MoEngage’s site, I could not rely on standard `requests`/`BeautifulSoup`. I used **Playwright** to simulate real user behavior and render the full page.
* I assume the user manually provides URLs that are accessible and are documentation pages.
* Only English content was considered.

---

## Design Decisions & Strategy

### Agent 1 - Analysis Agent

The `main.py` file runs the analysis pipeline orchestrated by `analysis_runner.py`. Each aspect of analysis (readability, structure, completeness, and style) is handled by a dedicated module. The logic is as follows:

* **Readability:**

  * Uses `textstat` to calculate metrics like Flesch Reading Ease.
  * Uses assess the content's readability from the perspective of a non-technical marketer.

* **Structure & Flow:**

  * Analyzes usage of headers, paragraph breaks, list formatting.
  * Highlights problems like large wall-of-text sections, missing headings, or unordered topics.

* **Completeness:**

  * Checks for presence of examples, context, and step-by-step instructions.
  * Flags when concepts are mentioned but not explained or supported.

* **Style Guidelines:**

  * Instead of a full Microsoft Style Guide, I focused on 3 core aspects:

    * Voice and Tone
    * Clarity and Conciseness
    * Action-Oriented Language

### Agent 2 - Revision Agent

This was the bonus task and I approached it as a hybrid system with layered logic:

1. **String-based Matching:**

   * First, the revision agent uses exact string matching to locate parts of the text that correspond to each suggestion.

2. **Fuzzy Matching (Fallback):**

   * If an exact match fails, I fall back to `fuzzywuzzy`-based approximate matching to locate the closest match.

3. **LLM Fallback (Final Layer):**

   * If fuzzy matching also fails (or yields low confidence), only then I use Gemini AI to rewrite or rephrase based on the suggestion.

This tiered fallback approach minimized LLM usage and made the revision process:

* More explainable
* Less expensive
* Easier to test/debug

The changes are applied in-place, and the updated content is saved to `revised_document.txt`.

---

## Challenges Faced

* **Scraping Blocked by Bot Protections:**

  * MoEngage docs use protections that block normal scraping. I switched to **Playwright** to emulate browser sessions and extract the full content.

* **Linking Suggestions to Text:**

  * The biggest pain point in Agent 2 was linking a vague suggestion like “Simplify this sentence” to the exact target text.
  * I addressed this using string matching + fuzzy matching before resorting to LLMs.

* **Balancing LLM Usage:**

  * Full LLM-based rewrites were too expensive and unpredictable. So I designed a system where LLMs are the last resort (for the Revision Agent).

---

## Architecture

```
documentation-analyzer/
├── agent-2.py               # Agent 2 - Revision Agent
├── main.py                  # Entry point to run Agent 1
├── analysis_report.json     # Output of Agent 1
├── revised_document.txt     # Output of Agent 2
├── analyzer/
│   ├── analysis_runner.py   # Orchestrates all analyzers
│   ├── readability_analyzer.py
│   ├── structure_analyzer.py
│   ├── completeness_analyzer.py
│   ├── style_analyzer.py
│   ├── prompts.py           # Prompt templates for LLM (minimal usage)
├── utils/
│   └── scraping.py          # Uses Playwright to extract full page content
└── requirements.txt
```

---

## Future Improvements

* Improve the **fuzzy match scoring** to handle longer sentences or paraphrased suggestions.

* Build a simple UI to visualize changes and accept/reject revisions manually.
* Refine prompt robustness based on model performance.

---

## Example output
Article 1

**URL:** `https://help.moengage.com/hc/en-us/articles/115003667986-Localize-Campaign-Messages#h_01JSDJJD6SQVJVKF63DTS5EZX3`

```json
{
  "url_analyzed": "https://help.moengage.com/hc/en-us/articles/115003667986-Localize-Campaign-Messages#h_01JSDJJD6SQVJVKF63DTS5EZX3",
  "readability_analysis": {
    "score": 7.2,
    "assessment": "The document is moderately readable but suffers from excessive redundancy and occasional verbosity. Sentence structures are mostly clear but can be tightened.",
    "suggestions": [
      {
        "description": "Reduce repetition of instructions across locales and examples.",
        "original": "Create new content: You must create new content for the campaign message.",
        "suggestion": "Create new campaign content for this locale."
      },
      {
        "description": "Replace verbose explanations with more concise statements.",
        "original": "Locales created for one-time and periodic campaigns in SMS, Email, and Push channels are refreshed every 6 hours.",
        "suggestion": "For SMS, Email, and Push campaigns, locale data refreshes every 6 hours."
      }
    ]
  },
  "structure_analysis": {
    "assessment": "The structure needs better hierarchy and fewer redundant subsections. Many headings repeat or overlap in content.",
    "suggestions": [
      "Avoid repeating the same step under different sections (like 'Create New Content').",
      "Merge duplicated H2 sections like 'Examplelink' and 'Channels and Delivery Types with Localization Supportlink' where content overlaps.",
      "Use consistent heading levels to reflect actual topic depth (e.g., don't jump from H1 to H6 arbitrarily)."
    ]
  },
  "completeness_analysis": {
    "assessment": "The documentation includes core concepts but lacks actionable examples and visuals for guidance.",
    "suggestions": [
      "Add a visual flowchart showing how localized content flows from campaign creation to delivery.",
      "Include a sample localized campaign with before/after message variations in different locales.",
      "Clarify how 'exclude users' affects targeting logic in real-world cases."
    ]
  },
  "style_analysis": {
    "assessment": "The tone is formal and informative but inconsistently switches between second person ('you') and passive instructions.",
    "suggestions": [
      "Stick with either second-person ('you') or imperative voice consistently.",
      "Avoid capitalizing section names mid-sentence (e.g., 'Step 2(content)').",
      "Remove outdated UI instructions that may change over time (e.g., 'Click + Locale in upper-right corner')."
    ]
  },
  "errors": []
}

```

Article 2 

**URL** : `https://help.moengage.com/hc/en-us/articles/33132363356564-View-Personalize-in-action#h_01JFAX3T5TMAWM1NZ1JTT4NP88`

```json
{
  "url_analyzed": "https://help.moengage.com/hc/en-us/articles/33132363356564-View-Personalize-in-action#h_01JFAX3T5TMAWM1NZ1JTT4NP88",
  "readability": {
    "score": "35.072287365813395",
    "assessment": "The content is informative but could benefit from improved clarity and consistency.",
    "suggestions": [
      {
        "description": "Inconsistent use of capitalization in headings.",
        "original": "Client-side personalization",
        "suggestion": "Client-Side Personalization"
      },
      {
        "description": "Long paragraphs may hinder readability.",
        "original": "Ready to witness the power of personalization? Follow our guide to explore the dynamic capabilities of MoEngage Personalize on our demo site...",
        "suggestion": "Break the paragraph into shorter sentences to enhance readability."
      }
    ]
  },
  "structure_and_flow": {
    "assessment": "The structure follows a logical sequence but lacks uniformity in formatting.",
    "suggestions": [
      {
        "description": "Inconsistent heading levels.",
        "original": "[H6] View Personalize in action",
        "suggestion": "Use consistent heading levels, e.g., [H2] View Personalize in Action"
      },
      {
        "description": "Steps and implementation sections are not clearly delineated.",
        "original": "[H3] Steps\nIf you are visiting from either of these geographies...",
        "suggestion": "Use bullet points or numbered lists for steps and separate implementation details under distinct subheadings."
      }
    ]
  },
  "completeness_of_information": {
    "assessment": "The guide covers various personalization scenarios but lacks detailed implementation instructions.",
    "suggestions": [
      {
        "description": "Missing links to referenced use case documents.",
        "original": "You can refer to this usecase doc to set up a similar experience.",
        "suggestion": "Provide direct links to the mentioned use case documents for user convenience."
      },
      {
        "description": "No screenshots or visuals to support the steps.",
        "original": "Visit the Furniture category. You can also view a few products...",
        "suggestion": "Include screenshots or diagrams to illustrate the steps and expected outcomes."
      }
    ]
  },
  "style_guidelines": {
    "assessment": "The content partially adheres to standard style guidelines.",
    "suggestions": [
      {
        "description": "Inconsistent formatting of product names.",
        "original": "Visit Brass Maang Tika & Gamebox product pages...",
        "suggestion": "Use consistent formatting for product names, e.g., italicize or quote them."
      },
      {
        "description": "Use of informal language.",
        "original": "Ready to witness the power of personalization?",
        "suggestion": "Adopt a more formal tone, e.g., 'Explore the capabilities of personalization.'"
      }
    ]
  },
  "errors": []
}

```
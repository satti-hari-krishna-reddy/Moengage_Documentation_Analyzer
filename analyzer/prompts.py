READABILITY_PROMPT = """
Analyze the following document text for readability, especially for a non-technical marketer.

The document includes markers like [H1], [H2], and "-" to indicate structure. DO NOT suggest changing or flagging these markers — they are intentional and part of the formatting.

Important context: This text may have minor formatting issues due to scraping (e.g., extra/missing spaces, occasional awkward breaks, or stray tags). You MUST IGNORE these and focus only on substantive readability issues. DO NOT flag these formatting artifacts.

Focus only on issues that significantly affect readability, such as:
- Long or overly complex sentences that could confuse a general reader.
- Technical jargon or unclear language that could be simplified.
- Sentences that could be rewritten to be more direct, clear, or reader-friendly.

Now, here is the REQUIRED format for your output. You MUST return a single JSON object with exactly two keys:

1. **"assessment"** — A short paragraph summarizing the overall readability quality of the input text.
2. **"suggestions"** — An array of suggestion objects, where each object includes:
   - "description": Brief explanation of the readability problem.
   - "original": The exact sentence or phrase from the text.
   - "suggestion": A clearer or simpler version of the original.

Your output MUST follow this JSON format strictly:

{{
  "assessment": "<your assessment here>",
  "suggestions": [
    {{
      "description": "<brief explanation>",
      "original": "<original sentence>",
      "suggestion": "<your rewritten version>"
    }},
    ...
  ]
}}

Instructions:

DO NOT return anything outside of the JSON structure.

DO NOT invent issues or overwhelm with low-impact suggestions.

Only include meaningful, high-impact readability improvements.

Prioritize clarity and quality over quantity.

Here is the Document Text:
{document_text}
"""


STRUCTURE_FLOW_PROMPT = """
Analyze the structure and flow of the following document.

The document uses [H1], [H2], etc. for headings. Use these markers to assess organization. DO NOT suggest changing or removing them.

Your job is to:
- Evaluate if the structure helps the reader navigate the content easily.
- Judge the logical progression from one section to another.
- Assess paragraph length, clarity of list formatting, and clarity of steps.

Due to scraping, ignore any weird spacing or broken lines — focus ONLY on structural logic.

Return output as a JSON object in this format:

  "assessment": "<summary of how well the structure supports comprehension>",
  "suggestions": "<actionable structural suggestion 1>, <actionable structural suggestion 2> ..."

**DO NOT include filler text or make unnecessary suggestions.**
Only include impactful suggestions that improve navigation, flow, or clarity.
Avoid suggestions that nitpick perfect structure or make redundant points.

Here is the Document Text:
{document_text}
"""

COMPLETENESS_PROMPT = """
Evaluate the completeness of the document in helping a reader fully understand and apply the concept or feature being discussed.

Focus on:
- Are all necessary steps and use cases clearly explained?
- Are there enough relevant examples?
- If something is missing, unclear, or could use an example — say so.

IGNORE minor formatting issues from scraping — only assess the depth and clarity of the actual content.

Return output as a JSON object in this format:

  "assessment": "<does the content feel complete and actionable?>",
  "suggestions": "A list of specific, actionable suggestions for improvement."

Do NOT make suggestions just to fill space. Be critical, but only when something is truly missing or unclear.

Here is the Document Text:
{document_text}
"""

STYLE_GUIDELINES_PROMPT = """
Evaluate this document's writing style based on simplified guidance from professional style guides like Microsoft's.

Focus on these areas only:
1. **Voice & Tone** — Is the tone helpful, clear, and user-focused?
2. **Clarity & Conciseness** — Are there any overly complex, technical, or bloated phrases?
3. **Action-Oriented Language** — Does it encourage user action clearly?

Only consider REAL language issues — NOT formatting. Ignore extra tags, line breaks, or spacing issues due to scraping.

Return output as a JSON object:

  "assessment": "<summary of how well the tone and style match a helpful user guide>",
  "suggestions": "A list of specific, actionable suggestions for improvement."

Make only valuable suggestions. DO NOT flood output with marginal or stylistic nitpicks.
Quality > Quantity.

Here is the Document Text:
{document_text}
"""
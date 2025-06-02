READABILITY_PROMPT = """
Analyze the following document text for readability, especially for a non-technical marketer.

The document includes markers like [H1], [H2], and "-" to indicate structure. DO NOT suggest changing these markers — they are intentional.

Due to scraping, the text may have occasional formatting issues such as missing spaces, stray tags, or awkward breaks. **DO NOT flag or comment on these formatting issues.** Only focus on substantive readability problems like:

- Long, complex, or technical sentences that a general reader may not follow.
- Sentences with unnecessary jargon, ambiguity, or awkward phrasing.
- Sentences that could be made more direct or reader-friendly.

You MUST return output as a list of JSON objects — ONE per readability issue.
Each must follow this format exactly:

{
  "description": "<what is hard to read and why>",
  "original": "<copy-paste exact sentence from input>",
  "suggestion": "<a clearer, friendlier version>"
}

**DO NOT invent problems or flood the output with low-priority or nitpicky suggestions.**
Only include real readability issues with meaningful impact.

Focus on quality, not quantity.

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

{
  "assessment": "<summary of how well the structure supports comprehension>",
  "suggestions": [
    "<actionable structural suggestion 1>",
    "<actionable structural suggestion 2>"
  ]
}

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

{
  "assessment": "<does the content feel complete and actionable?>",
  "suggestions": [
    "<where an example or detail could be added>",
    "<which concept needs clearer explanation>"
  ]
}

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

{
  "assessment": "<summary of how well the tone and style match a helpful user guide>",
  "suggestions": [
    {
      "description": "<what style issue you saw>",
      "original": "<original sentence>",
      "suggestion": "<a simpler, clearer rewrite>"
    }
  ]
}

Make only valuable suggestions. DO NOT flood output with marginal or stylistic nitpicks.
Quality > Quantity.

Here is the Document Text:
{document_text}
"""
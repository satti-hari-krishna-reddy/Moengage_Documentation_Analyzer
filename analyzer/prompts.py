READABILITY_PROMPT = """
Analyze the following document text to assess its readability for a non-technical marketer.
The document text includes markers like [H1], [H2] for headings, and '-' for list items.
Consider these markers when evaluating structure in relation to readability.

Your analysis should focus on:
- Language complexity (e.g., jargon, overly academic words)
- Sentence structure and length
- Clarity and directness of the language

You must return the output STRICTLY as a  list of JSON objects.
Each object should follow this format:

{{
  "description": "<brief explanation of the issue>",
  "original": "<the exact original sentence or phrase from the document>",
  "suggestion": "<your suggested replacement>"
}}

Only include necessary suggestions based on real issues. Do not make changes if the original sentence is already clear and accessible.

Please note: The document might contain formatting inconsistencies or stray tags due to scraping. Focus on fixing the actual readability issues and ignore some spacing issues or other things as again that was a scraped text so there might be some inconsistencies focus on other readability issues and dont be too verbose generating a lot of them rather focus on quality over quantity. so please avoid making verbose low impact suggestions.

Now, here is the Document Text:
{document_text}
"""


STRUCTURE_FLOW_PROMPT = """
Analyze the structure and flow of the following document text.
The document text includes markers like [H1], [H2] for headings, and '-' for list items.
Consider these markers explicitly in your analysis.

Your analysis should evaluate:
- Effectiveness of headings and subheadings in organizing content.
- Appropriateness of paragraph length.
- Use and formatting of lists.
- Logical progression of information from one section to the next.
- Ease of navigation and finding specific information.

Provide your output STRICTLY as a JSON object with the following keys:
- "assessment": A concise paragraph summarizing the overall structure and flow.
- "suggestions": A list of specific, actionable suggestions for improvement. For example: "The section under '[H2] Advanced Settings' lacks introductory context." or "Paragraph starting with '...' is too long (X lines/words) and should be broken down for better readability." or "Consider using a numbered list for the steps under '[H3] Installation Guide' instead of bullet points for clearer sequence."

If the document text largely adheres to the criteria for this section, state this in your assessment and provide minimal, if any, suggestions. Avoid making suggestions for the sake of it if the quality is already high.

Do NOT include any conversational filler, apologies, or commentary outside of the JSON object.
Only output the JSON object.
Focus heavily on making quality suggestions rather than being verbose always prefer those that can make the most impact rather than a lot of them so keep in mind quality >> quantity. so please avoid making verbose low impact suggestions.

Document Text:
{document_text}
"""

COMPLETENESS_PROMPT = """
Assess the completeness of information and examples in the following document text.
The document text includes markers like [H1], [H2] for headings, and '-' for list items.
Consider these markers when evaluating the context for completeness.

Your analysis should determine:
- If the article provides enough detail for a user to understand and implement the feature or concept discussed.
- If there are sufficient, clear, and relevant examples to aid understanding.
- Where examples are missing, unclear, or could be improved.

Provide your output STRICTLY as a JSON object with the following keys:
- "assessment": A concise paragraph summarizing the overall completeness of information and examples.
- "suggestions": A list of specific, actionable suggestions for improvement. For example: "The article explains feature Y but lacks a practical example of its common use cases." or "Consider adding a code snippet for the API integration described under '[H2] API Details'."

If the document text largely adheres to the criteria for this section, state this in your assessment and provide minimal, if any, suggestions. Avoid making suggestions for the sake of it if the quality is already high.

Do NOT include any conversational filler, apologies, or commentary outside of the JSON object.
Only output the JSON object.
Focus heavily on making quality suggestions rather than being verbose always prefer those that can make the most impact rather than a lot of them so keep in mind quality >> quantity, so please avoid making verbose low impact suggestions.


Document Text:
{document_text}
"""

STYLE_GUIDELINES_PROMPT = """
Analyze the following document text for adherence to simplified style guidelines.
The document text includes markers like [H1], [H2] for headings, and '-' for list items.

Your analysis should be guided by general principles from a well-known style guide, such as the Microsoft Style Guide, focusing on these key aspects:
1.  **Voice and Tone**: Is it customer-focused, consistently professional, clear, and concise? (e.g., Microsoft Style Guide emphasizes a friendly, helpful, and direct tone).
2.  **Clarity and Conciseness**: Are there overly complex sentences, jargon, or verbose phrasing that could be simplified? (e.g., Microsoft Style Guide advises against overly technical jargon for general audiences and prefers shorter sentences).
3.  **Action-oriented Language**: Does the text effectively guide the user and encourage action where appropriate? Are calls to action clear? (e.g., Microsoft Style Guide promotes using strong verbs and active voice for instructions).

Provide your output STRICTLY as a JSON object with the following keys:
- "assessment": A concise paragraph summarizing the overall adherence to these style guidelines, referencing the kind of principles you are applying.
- "suggestions": A list of specific, actionable suggestions for improvement. Each suggestion should identify the problematic text and propose a concrete change based on style guide principles. For example: "The sentence 'It is recommended that users...' uses passive voice; consider rephrasing to 'We recommend that you...' or 'You should...' in line with guidance on active voice." or "The term 'multifaceted' in paragraph X could be simplified to 'has many parts' or similar, for better clarity as advised by style guides."

If the document text largely adheres to the criteria for this section, state this in your assessment and provide minimal, if any, suggestions. Avoid making suggestions for the sake of it if the quality is already high.

Do NOT include any conversational filler, apologies, or commentary outside of the JSON object.
Only output the JSON object.
Focus heavily on making quality suggestions rather than being verbose always prefer those that can make the most impact rather than a lot of them so keep in mind quality >> quantity, so please avoid making verbose low impact suggestions.


Document Text:
{document_text}
"""

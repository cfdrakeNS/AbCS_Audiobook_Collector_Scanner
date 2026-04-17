
# AbCS Copilot Accessibility Protocol (Final - 2026-04-17)

**For JAWS/NVDA screen reader users:**
- Always provide factual summaries only: clearly state what changed and what will change, with no extra commentary.
- All instructions and code changes must be accessible and easy to follow for screen reader users.

- Only use ###START replace code and ###@END replace code markers in the source file when a large block of code (multiple functions, classes, or >10 lines) must be pasted by the user.
- For all other changes (small edits, logic fixes, or <10 lines), do NOT insert any markers—just make the change directly in the file.
- Never use code_scratch_pad for small or single-line changes.
- Never require the user to guess or search for code in code_scratch_pad unless a large block is being replaced.
- Always provide a clear, factual summary of what changed and why, so screen reader users can quickly understand the update.
- Reference: abcs_screen_reader_protocol.md

## Reference docs for AbCS accessibility (in doc/):
- PySide6_Accessibility_Patterns_and_Implementation_Reference
- pySide6_accessible_dialogue
- PySide6_Screen_Reader_Accessibility_Best_Practices

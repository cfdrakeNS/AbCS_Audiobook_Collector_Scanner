`### Factual Summary: AI Performance and VS Code Settings
* **AI Lockup Cause:** The extension often hangs when trying to process massive context (like 34,000+ records) or when generating massive code blocks. This "lockup" affects both the UI and screen reader responsiveness.
* **Output Protocol Adjustment:** To ensure stability, I will strictly avoid large code blocks in the chat panel. Changes will be provided as concise diffs or factual summaries as per `AGENTS.md`.
* **Recommended VS Code Settings:**
    1. **Index Limitation:** Ensure that `data/` (especially `.db` files) and `backups/` are listed in your `.gitignore` or excluded in VS Code's "Search: Exclude" settings. This prevents the AI from trying to index thousands of database entries, which causes the extension to freeze.
    2. **Extension Updates:** Verify the Gemini Code Assist extension is updated to the latest version to resolve memory leak issues.
* **Screen Reader Optimization:** By sticking to "Factual Summaries" first, we reduce the amount of text JAWS has to process in the virtual buffer, minimizing the chance of the VS Code window becoming "Not Responding."
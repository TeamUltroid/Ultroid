# Lessons Learned

- When users ask for follow-up fixes after a review, expand verification beyond syntax checks (e.g., run unit test suites and targeted plugin tests) before finalizing.
- Avoid exposing raw exception text in user-facing bot responses; keep details in logs and return concise actionable guidance.
- For location-hint branches (like `butler`), return immediately after sending the hint to avoid accidental follow-up API calls.

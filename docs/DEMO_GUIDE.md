# Instructor demonstration guide

Use this as a practice outline, adapting it to what you understand and personally verified. Do not claim the synthetic results describe current hiring.

1. **Purpose and scope.** Explain the three questions: comparable pay, language mentions, and locations in a job CSV. State that the included data is fictional.
2. **Data pipeline.** Open the CSV and explain one row. Show the input contract, duplicate handling, and why a missing salary does not delete a job.
3. **Interactive analysis.** Launch the app, select Remote and Python, and explain the changing denominators. Compare language any/all behavior.
4. **One calculation.** Explain $40–$60/hour → $50 midpoint → $104,000 annualized, under the 2,080-hour assumption. Explain why the median of these midpoints is not actual earnings.
5. **Transparency.** Open the records and quality report. Show a missing salary and a non-USD example. Download an export with provenance.
6. **Reliability.** Run tests or show an actual recorded test run. Explain one boundary-value test and one UI interaction test. State which manual checks you personally completed.
7. **Architecture and contribution.** Point to data, analytics, chart, and UI modules. Describe your actual changes and learning, distinguish assistance, and show real Git history.

Practice questions:

- Why use the median? How could reporting coverage change its interpretation?
- Why can language percentages sum above 100%?
- Why does JavaScript not count as Java?
- How would you adapt a licensed public dataset to this schema?
- What does an automated AppTest prove, and what still needs a real browser check?
- What limitation would you address next, and how would you test the change?

Personal rehearsal date: ________  Actual rehearsal time: ________

Questions I could explain confidently: ________

Questions needing more study: ________

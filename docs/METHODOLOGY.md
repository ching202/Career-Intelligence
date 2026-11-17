# Analysis methodology

## Research questions

1. What does the distribution of comparable salary ranges look like in a selected file?
2. Which programming/query languages are mentioned most often among its selected jobs?
3. Where are those jobs located, and what work arrangements do they describe?

These questions describe the loaded dataset. A representative, documented real dataset would be necessary for conclusions about the wider labor market. The bundled sample cannot provide those conclusions.

## Salary calculations

For a valid USD range with positive finite bounds and maximum ≥ minimum, annualize both bounds by period: annual 1; monthly 12; weekly 52; hourly 2,080. Take the midpoint of each annualized range, then compute the median across qualifying jobs. Equal bounds are allowed. One-sided ranges are excluded, not estimated.

Example: a fictional $40–$60/hour range has a $50/hour midpoint and $104,000 annualized midpoint. The assumption is 40 hours/week × 52 weeks/year. This is neither guaranteed earnings nor total compensation.

**Salary coverage** = jobs with usable USD ranges / all filtered jobs × 100. Show this denominator alongside salary summaries. A group median based on one observation is still shown with its sample count; it is not a reliable market benchmark. Currency conversion, taxes, inflation, equity, and cost-of-living adjustment are out of scope.

## Skill frequency

Split the explicit skills field on `;`, `|`, or `,`, trim spaces, and normalize known aliases. Count each canonical token once per job. Do not search title/description substrings: JavaScript must not count as Java; C++, C#, and C stay distinct.

**Skill share** = jobs mentioning the token / all filtered jobs × 100. Jobs with no skill tokens remain in the denominator. Multiple tokens per job mean shares can sum above 100%. These are mention frequencies, not vacancies attributable exclusively to one language or evidence of causal salary effects.

## Filters and time

All charts use one shared filtered frame. Choices within a category are OR; different categories are AND. Language matching offers explicit any/all semantics. Title/company search is case-insensitive literal text. Empty selections mean no restriction.

The salary threshold is an inclusive minimum annual midpoint. When **Include jobs without usable USD salaries** is checked, those jobs remain even if the threshold is positive. Uncheck it for a strict pay-only view.

Date bounds are inclusive. An incomplete date range is not applied. Undated jobs remain by default unless explicitly excluded while filtering by date. Posting activity groups dated records into Monday-start weeks and fills internal missing weeks with zero. Boundary weeks may be incomplete. This is file activity, not a growth-rate estimate.

## Locations and quality

Location strings are used as supplied after outer whitespace removal. The app does not merge geographic aliases or infer remote eligibility. A remote job may still have a city or country restriction. The Remote share metric counts records whose normalized work mode equals `Remote`.

Quality notes cover the full loaded file, not just the current filters. One row can have several notes. Notes identify logical CSV record numbers, job IDs, and actions. Duplicate IDs retain the first valid identity; different IDs referring to the same vacancy are not detected.

## Reproducibility and limitations

The deterministic generator, raw sample, dependency pins, tests, source hashes, and Git history preserve the build's provenance. Uploaded real data requires independent provenance and licensing records. Claims about real salaries, demand, geographic opportunity, or trends remain outside the synthetic demonstration's evidence.

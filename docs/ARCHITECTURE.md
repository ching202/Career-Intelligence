# Architecture and technical decisions

Career Intelligence uses a single Streamlit application with small Python modules. A database, API server, authentication system, and paid data provider would add complexity without helping this CSV-based MVP.

| Component | Responsibility | Depends on |
| --- | --- | --- |
| `data.py` | Bound input size; parse schema; normalize; return jobs plus audit rows | pandas, NumPy, standard library |
| `analytics.py` | Pure filters, aggregates, frequency counts, safe CSV output | pandas, data contract |
| `charts.py` | Format figures from computed values | Plotly |
| `app.py` | Widget state, dataset selection, messages, figures, downloads | Streamlit and the three modules |
| `generate_sample_data.py` | Deterministic fictional records | Standard library |
| `verify.py` | Run real checks; preserve outputs, versions, timestamps, hashes | pytest, coverage, standard library |

The app loads a bundled file or in-memory uploaded bytes. The data layer returns a `Dataset` with validated `jobs`, a quality `issues` frame, and input/dropped row counts. The UI builds an immutable `Filters` value and calls `filter_jobs`. All metrics, charts, tables, and record exports then derive from that filtered frame. Quality reports intentionally describe the entire input.

The bundled bytes are cached. Uploaded bytes are processed within the session and are neither shared through a global upload cache nor written to disk. A SHA-256 fingerprint detects a changed file and clears filter state so stale category selections cannot hide a new dataset. This fingerprint is not an authenticity check.

The data and analysis modules do not depend on Streamlit, making numerical behavior testable without a UI. Streamlit's own `AppTest` covers component rendering, state, and interactions. Upload integration tests supply in-memory file bytes at the uploader boundary; they do not claim a real browser file-picker test.

## Decisions and tradeoffs

| Decision | Reason / tradeoff |
| --- | --- |
| Synthetic default CSV | Free, reproducible, license-clear demonstration; cannot support real-market claims. |
| Explicit input schema | Reliable and easy to explain; arbitrary datasets need mapping first. |
| USD-only comparison | Avoids incorrect mixing of currencies; no currency conversion is attempted. |
| Midpoint + median | Simple transparent summary; does not estimate actual compensation. |
| Exact tokens | Prevents substring mistakes; does not infer skills from job descriptions. |
| Location labels, no map | Avoids geocoding services and guessed coordinates. |
| No upload persistence | Simple local privacy behavior; users must save their own exports. |
| Native Streamlit layout | Maintainable interface; visual browser checks are still needed on the target computer. |
| Pinned direct dependencies | Reproducible application APIs; installed transitive versions are recorded separately. |

Future work, if wanted after the practicum MVP: a licensed public-data importer, saved filter presets, stronger duplicate detection, and explicitly sourced time-series comparisons. None is required to run this version.

# Using Career Intelligence

## Starting at home

Download and extract the entire ZIP on your Windows computer. Read the root README and install Python 3.12. Double-click `START_WINDOWS.bat` or follow the PowerShell commands. The address `localhost:8501` means the computer running the app; opening it on a phone will not connect to a different PC automatically.

The app binds only to your computer by default. Public hosting and remote phone access are outside this MVP. No paid hosting is needed to run or present it on your PC.

## Reading the dashboard

The top metrics summarize the current filters. **Job records** counts retained jobs. **Median annual midpoint** uses only comparable pay. **Usable USD salary coverage** explains how much pay information supports that median. **Remote share** describes the work-arrangement field.

The **Overview** tab compares arrangements and experience and shows posting activity. **Salaries** shows midpoints and group medians with counts. **Languages** counts explicit tokens, with an option for frameworks and other skills. **Locations** compares supplied location labels. **Explore data** makes individual records inspectable.

Blank multiselects mean all values. Multiple selections in one filter match any selected value, except the explicit **All selected** language option. Different filter categories work together. A title search treats punctuation as literal text, not a pattern language.

CSV downloads reflect the current filters. The quality report describes the whole loaded file. Exports retain the dataset's provenance label. No uploaded file is persisted by the application.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| `py` or Python 3.12 is not found | Install Python 3.12, reopen the terminal, and repeat the README steps. |
| `No module named streamlit` | Install requirements using the same `.venv` Python used to launch the app. |
| PowerShell blocks activation | Use the provided direct `.venv\Scripts\python.exe` commands; activation is unnecessary. |
| Browser does not open | Visit `http://localhost:8501` while the terminal remains running. |
| Port 8501 is already in use | Stop the other app or launch with `--server.port 8502`, then visit that port. |
| An app window disappears after an error | Run the README commands in an open PowerShell window to read the error. |
| CSV missing required columns | Use the template and the data dictionary; arbitrary public CSVs need mapping. |
| Salary metric says N/A | Review the quality report for missing bounds, non-USD currency, invalid numbers, or unknown periods. |
| No jobs match | Reset filters; ensure selected languages/locations exist. |
| Date range does not apply | Choose both a start and an end date. |
| Sample shows unusual market results | The sample is invented for testing and demonstration, not market research. |

If you report a bug, include the action, expected result, actual result, and a small synthetic input that reproduces it. Do not include personal data or credentials.

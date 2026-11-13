# Historical pandas discrepancy: resolved parsing cause

## Evidence and scope

The user supplied a Databricks HTML export of `01_Opioid_Project_Data_Exploration` and identified the accompanying CSV files as the originals. The HTML's embedded base64/URL-encoded notebook model was decoded as JSON; no JavaScript, HTML instructions, or notebook code was executed. Selected relevant code and saved outputs, with the HTML SHA-256, are recorded in `analysis/pandas_notebook_evidence.json`. Cell indexes below are zero-based positions in the exported commands array.

The newly uploaded dispensing CSV SHA-256 is `8cd88e062cab18e28d7ec7baa85f77c392c4e29665fb2cc35878c80023608f4d`, identical to the frozen source CSV. The newly uploaded overdose CSV exceeds the tool's 32 MiB transfer limit. Its byte identity cannot be asserted. Reproduction used the previously supplied frozen overdose ZIP, which reproduces every historical validation target and all saved complete-case yearly counts. If byte-for-byte verification of the new overdose upload is required, supply it as a ZIP; this does not block diagnosing the demonstrated parsing failure.

## Cause

Exported cell 13 applies:

```python
# Historical behavior: comma-formatted observed counts are coerced to missing.
overdose_clean_pdf['Overdose_Deaths'] = pd.to_numeric(
    overdose_clean_pdf['Provisional Drug Overdose Deaths'], errors='coerce'
)
```

Pandas does not treat a string such as `"1,616"` as numeric under this conversion. `errors='coerce'` silently changes it to missing. This is a parsing error, not CDC suppression. The current PySpark pipeline already removes comma thousands separators before numeric conversion.

The corrected pandas equivalent is:

```python
# Normalize thousands separators while retaining true missing/suppressed values as missing.
raw_counts = overdose_clean_pdf['Provisional Drug Overdose Deaths'].astype('string')
overdose_clean_pdf['Overdose_Deaths'] = pd.to_numeric(
    raw_counts.str.replace(',', '', regex=False), errors='coerce'
)
```

The original production pipeline also rejects unrecognized tokens rather than silently accepting any malformed value; this corrected pandas example reproduces the historical approach with only comma normalization changed.

## Controlled reproduction

`analysis/reconcile_pandas.py` uses pandas 2.2.3 and the original read_csv defaults, year filtering, FIPS padding, December selection, deduplication, and inner join. It compares two runs that differ only in comma removal before numeric conversion. It does not execute code extracted from the HTML.

| Metric | Historical parsing | Comma-normalized parsing |
|---|---:|---:|
| Raw dispensing rows | 18,864 | 18,864 |
| Raw overdose rows | 226,368 | 226,368 |
| Matching county FIPS | 3,142 | 3,142 |
| Merged county-years | 15,710 | 15,710 |
| Complete observations | 8,180 | 8,203 |
| Complete-case counties | 2,385 | 2,388 |
| Missing dispensing | 297 | 297 |
| Missing overdose | 7,298 | 7,275 |

All eight historical targets are reproduced. The corrected values equal the current pipeline's validated results. The old `7,298` total included 23 parse failures alongside genuine missing/suppressed cells and should not be labeled exclusively as CDC missing/suppression.

| Year | Historical complete cases | Corrected complete cases | Recovered |
|---|---:|---:|---:|
| 2020 | 1,584 | 1,588 | 4 |
| 2021 | 1,689 | 1,694 | 5 |
| 2022 | 1,680 | 1,685 | 5 |
| 2023 | 1,668 | 1,674 | 6 |
| 2024 | 1,559 | 1,562 | 3 |

The 23 recovered county-years occur in six counties: Maricopa (04013), Los Angeles (06037), Cook (17031), Philadelphia (42101), Harris (48201), and King (53033). Maricopa, Los Angeles, and Cook are the three additional unique complete-case counties; the other three already had at least one complete year under the old parsing. Every recovered row contains a reported comma-formatted count and nonmissing dispensing, not an estimated suppressed value. The full row-level list is `analysis/pandas_reconciliation_rows.csv`.

## Decision and remaining provenance

Keep the current pipeline, dashboard, and research results: they already use the corrected parsing. Preserve the old targets as historical reproduction evidence, not desired corrected values. Their nonzero differences in the quality report are expected consequences of this identified defect; do not edit source values or zero-fill suppression to make them disappear.

The parsing cause is resolved for the reproduced notebook and frozen inputs. This does not recover original CDC export dates/releases, verify byte identity of the newly uploaded oversized overdose CSV, or fix prescriber-versus-resident geography. Those provenance/interpretation limitations remain separate. No new result or dashboard refresh is required to apply the parsing correction to this project, because it was already present.

## Reproduction

```bash
python -m pip install -r requirements-reconciliation.txt
python analysis/reconcile_pandas.py
python -m unittest discover -s tests -p 'test_*.py'
```

The script regenerates the metric JSON and row-level CSV. The tests cover the historical failure, corrected observed values, genuine missing values, reported zero, and full metric reproduction. Normal CI includes the pinned pandas reference dependency alongside PySpark; production processing remains PySpark.

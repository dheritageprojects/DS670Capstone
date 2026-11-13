# Pipeline architecture

```mermaid
flowchart LR
    A[CDC dispensing CSV] --> C[Unity Catalog Volume: original files]
    B[CDC provisional overdose CSV] --> C
    G[GitHub versioned notebooks and documentation] --> D[Codex development and checks]
    D --> E[Databricks PySpark notebook]
    C --> E
    E --> F[Normalize FIPS, dates, missing values]
    F --> H[Validate series and unique keys]
    H --> I[December annual counts and annual dispensing]
    I --> J[Full county-year panel with missingness flags]
    J --> K[Quality report and target comparison]
    J --> L[Databricks AI/BI dashboard]
```

Source retrieval is manual until exact CDC endpoints and release versions are confirmed. Record download dates and source release metadata with each run. Databricks credentials belong in secure settings, never in GitHub.

# Pipeline architecture

```mermaid
flowchart LR
    CDC[User-supplied CDC CSV snapshots] --> ZIP[GitHub frozen ZIPs and source manifest]
    ZIP --> SETUP[Pinned Databricks setup notebook]
    SETUP --> VOL[Unity Catalog source Volume]
    CODE[GitHub code and documentation] --> DEV[Codex development and CI checks]
    DEV --> PRIMARY[Databricks primary PySpark pipeline]
    VOL --> PRIMARY
    PRIMARY --> FULL[Full county-year coverage panel]
    PRIMARY --> COMMON[Common-key county-year panel]
    PRIMARY --> QUALITY[Quality report with target differences]
    FULL --> DASH[Original AI/BI dashboard page]
    QUALITY --> DASH
    VOL --> LIVE[Read-only strict sensitivity SQL]
    COMMON --> LIVE
    LIVE --> PAGE[Annualization sensitivity dashboard page]
    LIVE --> ANALYSIS[Year and cohort association/trend SQL]
    COMMON --> GEO[State-year descriptive SQL]
    ANALYSIS --> EXPORT[Full result exports and reference checks]
    GEO --> EXPORT
    EXPORT --> REPORT[Findings and capstone draft]
    VOL --> SENS[Sensitivity PySpark notebook]
    COMMON --> SENS
    SENS --> TABLES[Five verified sensitivity Delta tables]
```

The primary and sensitivity pipelines, persisted Delta outputs, and live SQL paths have now been verified in Databricks. Source/window parity and independent summary checks are documented in `sensitivity_verification.md`. Both dashboard pages have user-reported review. No publication or automated Databricks job scheduling is implied.

CDC source landing pages are now verified; exact export/download and snapshot release provenance remain incomplete. The bootstrap retrieves versioned GitHub snapshots, not live CDC endpoints. See `reproducibility.md` for version pins, execution order, overwrite behavior, access requirements, and recovery after partial runs. Source hashes identify exact bytes; they do not establish original publication provenance. Credentials belong in secure connection settings, never in Git.

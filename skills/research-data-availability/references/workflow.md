# Data Availability Workflow

## Data Record

Each dataset should have:

| Field | Meaning |
|---|---|
| Dataset ID | stable `DATA-*` ID |
| Name / Version | dataset version, split, or snapshot |
| Used By | `CLM-*`, `EXP-*`, figures, or tables |
| Path | local path, remote path, or archive path |
| Hash / Manifest | hash, manifest file, or reason unavailable |
| Access Level | public, private, restricted, or TBD |
| License / Permission | license, advisor permission, or project restriction |
| Data Dictionary | schema, labels, columns, units, classes |
| Generation Command | script or notebook that prepares processed data |

## Final Audit Rules

- P0: core thesis claim has no source data or output artifact.
- P0: result data path is fake, inaccessible, or contradicted by experiment records.
- P1: hash/manifest, access level, or license/permission is missing.
- P1: processed data cannot be regenerated from recorded commands.
- P2: data dictionary is incomplete but claim traceability is otherwise clear.

## Recommended Script

```bash
python scripts/audit_data_availability.py --warn-only
```

Use strict mode before final submission or defense.


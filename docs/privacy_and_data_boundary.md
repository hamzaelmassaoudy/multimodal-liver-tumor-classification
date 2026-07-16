# Privacy and data boundary

## Public contents

The repository contains source code, configuration templates, cleared notebooks, synthetic-data tests, methodological documentation, and cohort-level aggregate results. Released aggregates do not contain patient rows or reversible membership information.

## Excluded patient-level material

The following must remain outside the repository:

- Raw or processed CT, DICOM, NIfTI, NPZ, or mask files.
- Patient identifiers, clinical rows, dates, accession numbers, hospital identifiers, or DICOM UIDs.
- Patient-level split membership, labels, predictions, probabilities, crop-retention records, or feature matrices.
- Historical checkpoints or derived artifacts that are unavailable or not approved for public distribution.

Public source datasets must be obtained from their custodians. Their availability does not grant this project permission to redistribute them.

## Local configuration

Private locations are resolved through environment variables referenced by [`configs/paths.example.yaml`](../configs/paths.example.yaml). Store actual locations in the ignored `configs/paths.yaml` or in the local process environment. Do not commit credentials, access tokens, signed download URLs, cloud mounts, machine-specific directories, or authentication output.

## Aggregate-only reporting

The C2 retention audit, internal metric utility, and external sex-scenario utility can consume authorized local inputs. Their publishable products are aggregate summaries only. Before sharing any new output, verify that it contains no identifiers, filenames, small-cell row detail, or patient-level values.

## Security reporting

If sensitive material or a credential is discovered in a clone or release, stop distribution, preserve evidence without reposting the value, and follow [`SECURITY.md`](../SECURITY.md). Do not open a public issue containing the sensitive content.

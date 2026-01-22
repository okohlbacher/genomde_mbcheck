# Meldebestaetigung Library Specification

> **Note:** This is a functional specification designed to be used with Claude Code for automated code generation and maintenance.

## Overview

A Python library to convert the string representation
(MB Format) to an internal representation, export it
in a JSON format, or write out a clear text representation
(__repr__). Based on this library, a simple command line
tool can create the JSON and text representation of a string
that can be passed on via the command line to stdout.

## Implementation Status

- [x] Core library (`meldebestaetigung.py`)
- [x] Command line interface (`mbcheck.py`)
- [x] JSON export functionality
- [x] Text representation (__repr__)
- [x] Syntax validation with warnings
- [x] SHA256 hash computation
- [x] CSV file input support with configurable column selection
- [x] Python package configuration (`pyproject.toml`)
- [x] Documentation (`README.md`)
- [x] License file (`LICENSE`)

## Requirements

- Python 3.9+
- No external dependencies (uses only standard library)

## Project Structure

```
meldebestaetigung/
├── meldebestaetigung.py   # Core library with Meldebestaetigung class
├── mbcheck.py             # Command line interface
├── pyproject.toml         # Python package configuration
├── README.md              # Documentation for GitHub
├── LICENSE                # MIT License
├── Spec.md                # This specification file
├── Examples/              # Example CSV files for testing
└── Tech Spec/             # Reference documentation (PDFs)
```

## Command Line Interface (mbcheck)

The CLI tool `mbcheck` supports two input modes:

### Single MB String
```bash
mbcheck "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1"
```

### CSV File Input
```bash
mbcheck --csv meldungen.csv
```

### CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--csv DATEI` | | Read EDIFACT format strings from CSV file |
| `--column NAME` | `-C` | Column name for MB strings (default: "Meldebestaetigung") |
| `--column-number NR` | `-N` | Column number, 1-based (default: 2) |
| `--tan-column NAME` | `-T` | Column name for TAN (default: "Vorgangsnummer") |
| `--tan-column-number NR` | | Column number for TAN, 1-based (default: 1) |
| `--json` | `-j` | Output as JSON (default) |
| `--text` | `-t` | Output as human-readable text |
| `--hash` | `-H` | Output only SHA256 hash |
| `--compact` | `-c` | Compact JSON without indentation |
| `--quiet` | `-q` | Suppress validation warnings |

### CSV File Format

The CSV file should have:
- A header row with column names
- TAN (Transaction Authentication Number) in the "Vorgangsnummer" column (or column 1)
- EDIFACT format strings in the "Meldebestaetigung" column (or column 2)

Example CSV structure:
```csv
Vorgangsnummer,Meldebestaetigung
b31bb6c8fe6d1566704ee34a8140600c0f3c051d3fd94e26ea9d432ecc686f02,IBE+1N4I391IHS+1N4I391IHS&20260122005&000000000&000000000&0&O&9&1&C&3&1+9+0241af4ce0f96120d99128d3092f6f6b9387c979fa9d7cdd1c32e6d73d2c6a28
```

## Data Formats

### MB Format
The format of a 'Meldebestaetigung' is an ASCII string
described in the Document
"Tech Spec/Dokumentation-Meldebestaetigung-MV-GenomSeq.pdf"
(in German)

The MB Format consists of 11 fields separated by `&`:

| # | Field | Format | Description |
|---|-------|--------|-------------|
| 1 | Alphanumerischer Code | an10 | 10-character alphanumeric code |
| 2 | Leistungsdatum + Zaehler | n11 | Date (YYYYMMDD) + 3-digit counter |
| 3 | Leistungserbringer-ID | an9 | Institution ID |
| 4 | Datenknoten-ID | an9 | Data node ID |
| 5 | Typ der Meldung | n1 | Report type (0-3, 9) |
| 6 | Indikationsbereich | a1 | Indication area (O, R, H) |
| 7 | Produktzuordnung | n1 | Product assignment (9) |
| 8 | Kostentraeger | n1 | Cost bearer (1-4) |
| 9 | Art der Daten | a1 | Data type (C, G) |
| 10 | Art der Sequenzierung | n1 | Sequencing type (0-4) |
| 11 | Qualitaetskontrolle | n1 | QC result (0, 1) |

### JSON Format
The fields and their structure follow
"Tech Spec/Techn-spezifikation-datensatz-mvgenomseq.pdf"
(in German)

The JSON output includes both raw codes and German descriptions
for each coded field.

### Text representation
A clear text description in German of the various
fields and their descriptive field values based on
the JSON Format description document.

## Error Handling

- [x] Check the syntax of the MB string - print a warning if incorrect
- [x] Validate field lengths and formats
- [x] Validate coded field values against allowed values
- [x] Validate date format within leistungsdatum_zaehler
- [x] Collect warnings without blocking parsing

## License

MIT License

Copyright (c) 2025 Oliver Kohlbacher

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

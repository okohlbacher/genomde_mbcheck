# genomDE_mbcheck - MV GenomSeq MB Format Parser

A Python library and CLI tool to parse, validate, and convert MB Format strings (Meldebestätigung) used in the German Genomic Sequencing Model Project (Modellvorhaben Genomsequenzierung nach Paragraf 64e SGB V).

## Features

- Parse MB Format strings into structured Python objects
- Export to JSON format with descriptive field values
- Human-readable German text representation
- Syntax validation with warnings
- SHA256 hash computation
- Command-line interface for quick conversions
- CSV file batch processing support

## Installation

```bash
pip install genomDE_mbcheck
```

Or install from source:

```bash
git clone https://github.com/kohlbacherlab/genomDE_mbcheck.git
cd genomDE_mbcheck
pip install -e .
```

## Requirements

- Python 3.9+
- No external dependencies (uses only standard library)

## Quick Start

### As a Library

```python
from genomDE_mbcheck import Meldebestaetigung, parse_mb_string

# Parse an MB Format string
mb_string = "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1"
mb = Meldebestaetigung.from_string(mb_string)

# Or use the convenience function
mb = parse_mb_string(mb_string)

# Get JSON representation
print(mb.to_json())

# Get human-readable text representation
print(repr(mb))

# Compute SHA256 hash
print(mb.compute_hash())

# Access individual fields
print(f"Code: {mb.alphanumerischer_code}")
print(f"Meldungstyp: {mb.meldungstyp}")
```

### As a Command-Line Tool

```bash
# Output JSON (default)
mbcheck "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1"

# Output human-readable text
mbcheck --text "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1"

# Output only the SHA256 hash
mbcheck --hash "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1"

# Compact JSON output
mbcheck --compact "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1"

# Suppress validation warnings
mbcheck --quiet "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1"
```

### CSV File Processing

Process multiple EDIFACT format strings from a CSV file:

```bash
# Process CSV file (uses column "Meldebestaetigung" or column 2 by default)
# TAN is read from column "Vorgangsnummer" or column 1 by default
mbcheck --csv meldungen.csv

# Specify a different column name for MB strings
mbcheck --csv meldungen.csv --column MB_Feld

# Specify column by number (1-based)
mbcheck --csv meldungen.csv --column-number 3

# Specify a different TAN column
mbcheck --csv meldungen.csv --tan-column TransaktionsNr

# Specify TAN column by number (1-based)
mbcheck --csv meldungen.csv --tan-column-number 1

# Combine with output format options
mbcheck --csv meldungen.csv --text --quiet
```

The CSV file is expected to have a header row. By default, the tool looks for:
- MB strings in column "Meldebestaetigung" (or column 2)
- TAN (Vorgangsnummer) in column "Vorgangsnummer" (or column 1)

## MB Format Specification

The MB Format (Meldebestätigung) is a string of 11 fields separated by `&`:

| # | Field | Format | Description |
|---|-------|--------|-------------|
| 1 | Alphanumerischer Code | an10 | 10-character alphanumeric confirmation code |
| 2 | Leistungsdatum + Zaehler | n11 | Date (YYYYMMDD) + 3-digit counter (ZZZ) |
| 3 | Leistungserbringer-ID | an9 | Institution ID per Paragraf 293 SGB V |
| 4 | Datenknoten-ID | an9 | Data node ID (KDKXXnnnn or GRZXXXnnn) |
| 5 | Typ der Meldung | n1 | 0=Initial, 1=Follow-Up, 2=Late, 3=Correction, 9=Test |
| 6 | Indikationsbereich | a1 | O=Oncological, R=Rare diseases, H=Hereditary |
| 7 | Produktzuordnung | n1 | 9=MV GenomSeq |
| 8 | Kostentraeger | n1 | 1=GKV, 2=PKV, 3=PKV/Beihilfe, 4=Other |
| 9 | Art der Daten | a1 | C=Clinical, G=Genomic |
| 10 | Art der Sequenzierung | n1 | 0=None, 1=WGS, 2=WES, 3=Panel, 4=WGS_LR |
| 11 | Qualitaetskontrolle | n1 | 0=Failed, 1=Passed |

### Example

```
MB String:  A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1
SHA256:     bad8a31b1759b565bee3d283e68af38e173499bfcce2f50691e7eddda62b2f31
```

## JSON Output Format

```json
{
  "alphanumerischer_code": "A123456789",
  "leistungsdatum": "2024-07-01",
  "zaehler": 1,
  "leistungserbringer_id": "260530103",
  "datenknoten_id": "KDKK00001",
  "meldungstyp": {
    "code": "0",
    "bezeichnung": "Erstmeldung"
  },
  "indikationsbereich": {
    "code": "O",
    "bezeichnung": "Onkologische Erkrankungen"
  },
  "produktzuordnung": {
    "code": "9",
    "bezeichnung": "MV GenomSeq"
  },
  "kostentraeger": {
    "code": "1",
    "bezeichnung": "GKV (Gesetzliche Krankenversicherung)"
  },
  "art_der_daten": {
    "code": "C",
    "bezeichnung": "Klinische Daten"
  },
  "art_der_sequenzierung": {
    "code": "2",
    "bezeichnung": "WES (Whole Exome Sequencing)"
  },
  "qualitaetskontrolle": {
    "code": "1",
    "bezeichnung": "Bestanden"
  },
  "mb_string": "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1",
  "hash": "bad8a31b1759b565bee3d283e68af38e173499bfcce2f50691e7eddda62b2f31"
}
```

## Text Output Format

```
============================================================
MELDEBESTÄTIGUNG (MV GenomSeq)
============================================================

Alphanumerischer Code:    A123456789
Leistungsdatum:           01.07.2024
Zähler:                   001
Leistungserbringer-ID:    260530103
Datenknoten-ID:           KDKK00001

Meldungstyp:              Erstmeldung (0)
Indikationsbereich:       Onkologische Erkrankungen (O)
Produktzuordnung:         MV GenomSeq (9)
Kostenträger:             GKV (Gesetzliche Krankenversicherung) (1)
Art der Daten:            Klinische Daten (C)
Art der Sequenzierung:    WES (Whole Exome Sequencing) (2)
Qualitätskontrolle:       Bestanden (1)

------------------------------------------------------------
MB-String: A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1
SHA256:    bad8a31b1759b565bee3d283e68af38e173499bfcce2f50691e7eddda62b2f31
============================================================
```

## Validation

The library performs syntax validation and issues warnings for:
- Invalid characters (only `[a-zA-Z0-9&]` allowed)
- Incorrect field lengths
- Invalid field values (e.g., unknown codes)
- Invalid date formats

Warnings are printed to stderr but do not prevent parsing. Access warnings programmatically:

```python
mb = parse_mb_string(mb_string)
for warning in mb.warnings:
    print(warning)
```

## API Reference

### Meldebestaetigung Class

#### Class Methods

- `from_string(mb_string: str) -> Meldebestaetigung`: Parse an MB Format string

#### Instance Methods

- `to_mb_string() -> str`: Convert back to MB Format string
- `compute_hash() -> str`: Compute SHA256 hash
- `to_dict() -> dict`: Convert to dictionary
- `to_json(indent: int = 2) -> str`: Convert to JSON string

#### Properties

- `warnings`: List of validation warnings
- All 11 fields as attributes

### Convenience Functions

- `parse_mb_string(mb_string: str) -> Meldebestaetigung`: Parse an MB Format string

## Related Documentation

This library implements the MB Format as specified in the official genomDE documentation:

- **Official BfArM Documentation**: [Modellvorhaben Genomsequenzierung - Informationen und Downloads](https://www.bfarm.de/DE/Das-BfArM/Aufgaben/Modellvorhaben-Genomsequenzierung/Informationen-und-downloads/_node.html)
- Dokumentation-Meldebestaetigung-MV-GenomSeq.pdf (Version 01.1, valid from 01.11.2025)
- Techn-spezifikation-datensatz-mvgenomseq.pdf (Version 1.2, 05.09.2025)

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Oliver Kohlbacher

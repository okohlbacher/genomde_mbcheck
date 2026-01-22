#!/usr/bin/env python3
"""
Command Line Interface for the Meldebestätigung (MB Format) Parser.

This CLI tool parses MB Format strings and outputs JSON or text representation.
Supports both command-line input and CSV file processing.
"""

from __future__ import annotations

import argparse
import csv
import sys

from Meldebestaetigung import parse_mb_string

DEFAULT_COLUMN_NAME = "Meldebestaetigung"
DEFAULT_COLUMN_NUMBER = 2  # 1-based column number


def process_mb_string(mb_string: str, args) -> dict:
    """
    Process a single MB string and return result dict.

    Returns a dict with 'success', 'input', 'output', and optionally 'error' keys.
    """
    result = {"input": mb_string, "success": False}

    try:
        mb = parse_mb_string(mb_string)

        if args.hash:
            result["output"] = mb.compute_hash()
        elif args.text:
            result["output"] = repr(mb)
        else:
            # JSON output
            indent = None if args.compact else 2
            result["output"] = mb.to_json(indent=indent)

        result["success"] = True

    except ValueError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Unerwarteter Fehler: {e}"

    return result


def process_csv_file(filepath: str, column_name: str, column_number: int, args) -> list[dict]:
    """
    Process a CSV file containing MB format strings.

    Args:
        filepath: Path to the CSV file
        column_name: Column name to look for (used if CSV has header)
        column_number: 1-based column number (used if CSV has no header or column name not found)
        args: Parsed command line arguments

    Returns:
        List of result dicts with 'row', 'success', 'input', 'output'/'error' keys.
    """
    results = []
    col_idx = column_number - 1  # Convert to 0-based index

    with open(filepath, newline='', encoding='utf-8') as csvfile:
        # Detect if file has a header by checking first line
        sample = csvfile.read(4096)
        csvfile.seek(0)

        try:
            has_header = csv.Sniffer().has_header(sample)
        except csv.Error:
            has_header = False

        if has_header:
            reader = csv.DictReader(csvfile)

            if not reader.fieldnames:
                raise ValueError("CSV-Datei hat keine Spalten")

            # Try to find the column by name, fall back to column number
            if column_name in reader.fieldnames:
                col_name = column_name
            elif col_idx < len(reader.fieldnames):
                col_name = reader.fieldnames[col_idx]
            else:
                raise ValueError(
                    f"Spalte '{column_name}' nicht gefunden und Spalte {column_number} "
                    f"existiert nicht (nur {len(reader.fieldnames)} Spalten vorhanden)"
                )

            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                mb_string = row.get(col_name, "").strip()
                if mb_string:  # Skip empty rows
                    result = process_mb_string(mb_string, args)
                    result["row"] = row_num
                    results.append(result)
        else:
            # No header - use column number
            reader = csv.reader(csvfile)

            for row_num, row in enumerate(reader, start=1):
                if row and len(row) > col_idx:
                    mb_string = row[col_idx].strip()
                    if mb_string:  # Skip empty rows
                        result = process_mb_string(mb_string, args)
                        result["row"] = row_num
                        results.append(result)

    return results


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Meldebestätigung (MB Format) Parser - Konvertiert MB-Strings in JSON oder Textdarstellung",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Beispiele:
  %(prog)s "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1"
  %(prog)s --json "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1"
  %(prog)s --text "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1"
  %(prog)s --hash "A123456789&20240701001&260530103&KDKK00001&0&O&9&1&C&2&1"
  %(prog)s --csv meldungen.csv
  %(prog)s --csv meldungen.csv --column MB_Feld
  %(prog)s --csv meldungen.csv --column-number 3

Standard-Spalte: "{DEFAULT_COLUMN_NAME}" (Spalte {DEFAULT_COLUMN_NUMBER})
        """
    )

    # Input source: either positional argument or CSV file
    parser.add_argument(
        "mb_string",
        nargs="?",
        help="Der MB-Format String (11 Felder getrennt durch '&')"
    )

    parser.add_argument(
        "--csv",
        metavar="DATEI",
        help="CSV-Datei mit MB-Format Strings einlesen"
    )

    parser.add_argument(
        "--column", "-C",
        metavar="NAME",
        default=DEFAULT_COLUMN_NAME,
        help=f"Spaltenname für MB-Strings in CSV (Standard: '{DEFAULT_COLUMN_NAME}')"
    )

    parser.add_argument(
        "--column-number", "-N",
        metavar="NR",
        type=int,
        default=DEFAULT_COLUMN_NUMBER,
        help=f"Spaltennummer (1-basiert) für MB-Strings in CSV (Standard: {DEFAULT_COLUMN_NUMBER})"
    )

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--json", "-j",
        action="store_true",
        help="Ausgabe im JSON-Format (Standard)"
    )
    output_group.add_argument(
        "--text", "-t",
        action="store_true",
        help="Ausgabe als Klartext-Beschreibung"
    )
    output_group.add_argument(
        "--hash", "-H",
        action="store_true",
        help="Nur den SHA256-Hash ausgeben"
    )

    parser.add_argument(
        "--compact", "-c",
        action="store_true",
        help="Kompakte JSON-Ausgabe ohne Einrückung"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Warnungen unterdrücken"
    )

    args = parser.parse_args()

    # Validate input source
    if args.csv is None and args.mb_string is None:
        parser.error("Entweder MB-String als Argument oder --csv DATEI angeben")

    if args.csv is not None and args.mb_string is not None:
        parser.error("Nicht beide: MB-String und --csv DATEI angeben")

    if args.column_number < 1:
        parser.error("Spaltennummer muss >= 1 sein")

    # Suppress warnings if requested
    if args.quiet:
        import warnings
        warnings.filterwarnings("ignore")

    # Process CSV file
    if args.csv:
        try:
            results = process_csv_file(args.csv, args.column, args.column_number, args)

            # Output results
            success_count = sum(1 for r in results if r["success"])
            error_count = len(results) - success_count

            for result in results:
                if result["success"]:
                    print(f"--- Zeile {result['row']} ---")
                    print(result["output"])
                    print()
                else:
                    print(f"--- Zeile {result['row']} (Fehler) ---", file=sys.stderr)
                    print(f"Eingabe: {result['input']}", file=sys.stderr)
                    print(f"Fehler: {result['error']}", file=sys.stderr)
                    print(file=sys.stderr)

            # Summary
            print(f"Verarbeitet: {len(results)} Einträge, {success_count} erfolgreich, {error_count} Fehler",
                  file=sys.stderr)

            if error_count > 0:
                sys.exit(1)

        except FileNotFoundError:
            print(f"Fehler: CSV-Datei nicht gefunden: {args.csv}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Fehler: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unerwarteter Fehler: {e}", file=sys.stderr)
            sys.exit(1)

    # Process single MB string
    else:
        try:
            mb = parse_mb_string(args.mb_string)

            if args.hash:
                print(mb.compute_hash())
            elif args.text:
                print(repr(mb))
            else:
                # Default to JSON output
                indent = None if args.compact else 2
                print(mb.to_json(indent=indent))

        except ValueError as e:
            print(f"Fehler: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unerwarteter Fehler: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()

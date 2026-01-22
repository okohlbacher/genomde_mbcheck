"""
Meldebestätigung (MB Format) Parser Library

A Python library to convert the string representation (MB Format) to an internal
representation, export it in JSON format, or write out a clear text representation.

Based on the specification from:
- Dokumentation-Meldebestaetigung-MV-GenomSeq.pdf
- Techn-spezifikation-datensatz-mvgenomseq.pdf
"""

import json
import hashlib
import re
import warnings
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


# Field value mappings for descriptive text
MELDUNGSTYP = {
    "0": "Erstmeldung",
    "1": "Follow-Up",
    "2": "Nachmeldung",
    "3": "Korrektur",
    "9": "Test",
}

INDIKATIONSBEREICH = {
    "O": "Onkologische Erkrankungen",
    "R": "Seltene Erkrankungen",
    "H": "Hereditäres Tumorsyndrom",
}

PRODUKTZUORDNUNG = {
    "9": "MV GenomSeq",
}

KOSTENTRAEGER = {
    "1": "GKV (Gesetzliche Krankenversicherung)",
    "2": "PKV (Private Krankenversicherung)",
    "3": "PKV/Beihilfe",
    "4": "Andere",
}

ART_DER_DATEN = {
    "C": "Klinische Daten",
    "G": "Genomische Daten",
}

ART_DER_SEQUENZIERUNG = {
    "0": "Keine Sequenzierung",
    "1": "WGS (Whole Genome Sequencing)",
    "2": "WES (Whole Exome Sequencing)",
    "3": "Panel-Sequenzierung",
    "4": "WGS_LR (Long-Read Whole Genome Sequencing)",
}

QUALITAETSKONTROLLE = {
    "0": "Nicht bestanden",
    "1": "Bestanden",
}


@dataclass
class Meldebestaetigung:
    """
    Represents a Meldebestätigung (confirmation of report) in the MB Format.

    The MB Format is a string of 11 fields separated by '&' characters.
    """

    alphanumerischer_code: str  # an10 - Alphanumeric code
    leistungsdatum_zaehler: str  # n11 - Service date + counter (JJJJMMTTZZZ)
    leistungserbringer_id: str  # an9 - Service provider ID (Institutionskennzeichen)
    datenknoten_id: str  # an9 - Data node ID
    meldungstyp: str  # n1 - Report type
    indikationsbereich: str  # a1 - Indication area
    produktzuordnung: str  # n1 - Product assignment
    kostentraeger: str  # n1 - Cost bearer/payer
    art_der_daten: str  # a1 - Type of data
    art_der_sequenzierung: str  # n1 - Type of sequencing
    qualitaetskontrolle: str  # n1 - Quality control result

    # Parsed components
    _leistungsdatum: Optional[datetime] = None
    _zaehler: Optional[int] = None
    _warnings: list = None

    def __post_init__(self):
        """Initialize parsed components and validate the data."""
        self._warnings = []
        self._parse_leistungsdatum_zaehler()

    def _parse_leistungsdatum_zaehler(self):
        """Parse the combined date and counter field."""
        if len(self.leistungsdatum_zaehler) == 11:
            try:
                date_str = self.leistungsdatum_zaehler[:8]
                self._leistungsdatum = datetime.strptime(date_str, "%Y%m%d")
                self._zaehler = int(self.leistungsdatum_zaehler[8:])
            except ValueError:
                self._warnings.append(
                    f"Ungültiges Leistungsdatum/Zähler Format: {self.leistungsdatum_zaehler}"
                )

    @classmethod
    def from_string(cls, mb_string: str) -> "Meldebestaetigung":
        """
        Parse an MB Format string and create a Meldebestaetigung instance.

        Args:
            mb_string: The MB Format string (11 fields separated by '&')

        Returns:
            A Meldebestaetigung instance

        Raises:
            ValueError: If the string format is invalid
        """
        validation_warnings = cls._validate_syntax(mb_string)

        parts = mb_string.split("&")
        if len(parts) != 11:
            raise ValueError(
                f"MB Format erwartet 11 Felder, aber {len(parts)} gefunden"
            )

        instance = cls(
            alphanumerischer_code=parts[0],
            leistungsdatum_zaehler=parts[1],
            leistungserbringer_id=parts[2],
            datenknoten_id=parts[3],
            meldungstyp=parts[4],
            indikationsbereich=parts[5],
            produktzuordnung=parts[6],
            kostentraeger=parts[7],
            art_der_daten=parts[8],
            art_der_sequenzierung=parts[9],
            qualitaetskontrolle=parts[10],
        )

        # Add syntax validation warnings
        instance._warnings.extend(validation_warnings)

        # Print warnings if any
        for warning in instance._warnings:
            warnings.warn(warning, UserWarning)

        return instance

    @classmethod
    def _validate_syntax(cls, mb_string: str) -> list:
        """
        Validate the syntax of an MB Format string.

        Args:
            mb_string: The MB Format string to validate

        Returns:
            A list of warning messages for any syntax issues found
        """
        validation_warnings = []

        # Check allowed characters
        allowed_pattern = re.compile(r'^[a-zA-Z0-9&]+$')
        if not allowed_pattern.match(mb_string):
            validation_warnings.append(
                "MB String enthält ungültige Zeichen. Erlaubt sind nur: [a-z][A-Z][0-9][&]"
            )

        parts = mb_string.split("&")
        if len(parts) != 11:
            validation_warnings.append(
                f"MB Format erwartet 11 Felder, aber {len(parts)} gefunden"
            )
            return validation_warnings

        # Validate individual fields
        # Field 1: Alphanumerischer Code (an10)
        if len(parts[0]) != 10:
            validation_warnings.append(
                f"Alphanumerischer Code muss 10 Zeichen haben, hat aber {len(parts[0])}"
            )

        # Field 2: Leistungsdatum + Zähler (n11)
        if len(parts[1]) != 11 or not parts[1].isdigit():
            validation_warnings.append(
                f"Leistungsdatum+Zähler muss 11 Ziffern haben (JJJJMMTTZZZ): {parts[1]}"
            )

        # Field 3: ID des Leistungserbringers (an9)
        if len(parts[2]) != 9:
            validation_warnings.append(
                f"Leistungserbringer-ID muss 9 Zeichen haben, hat aber {len(parts[2])}"
            )

        # Field 4: ID des Datenknoten (an9)
        if len(parts[3]) != 9:
            validation_warnings.append(
                f"Datenknoten-ID muss 9 Zeichen haben, hat aber {len(parts[3])}"
            )

        # Field 5: Typ der Meldung (n1)
        if parts[4] not in MELDUNGSTYP:
            validation_warnings.append(
                f"Ungültiger Meldungstyp '{parts[4]}'. Erlaubt: {list(MELDUNGSTYP.keys())}"
            )

        # Field 6: Indikationsbereich (a1)
        if parts[5] not in INDIKATIONSBEREICH:
            validation_warnings.append(
                f"Ungültiger Indikationsbereich '{parts[5]}'. Erlaubt: {list(INDIKATIONSBEREICH.keys())}"
            )

        # Field 7: Produktzuordnung (n1)
        if parts[6] not in PRODUKTZUORDNUNG:
            validation_warnings.append(
                f"Ungültige Produktzuordnung '{parts[6]}'. Erlaubt: {list(PRODUKTZUORDNUNG.keys())}"
            )

        # Field 8: Kostenträger (n1)
        if parts[7] not in KOSTENTRAEGER:
            validation_warnings.append(
                f"Ungültiger Kostenträger '{parts[7]}'. Erlaubt: {list(KOSTENTRAEGER.keys())}"
            )

        # Field 9: Art der Daten (a1)
        if parts[8] not in ART_DER_DATEN:
            validation_warnings.append(
                f"Ungültige Art der Daten '{parts[8]}'. Erlaubt: {list(ART_DER_DATEN.keys())}"
            )

        # Field 10: Art der Sequenzierung (n1)
        if parts[9] not in ART_DER_SEQUENZIERUNG:
            validation_warnings.append(
                f"Ungültige Art der Sequenzierung '{parts[9]}'. Erlaubt: {list(ART_DER_SEQUENZIERUNG.keys())}"
            )

        # Field 11: Ergebnis der Qualitätskontrolle (n1)
        if parts[10] not in QUALITAETSKONTROLLE:
            validation_warnings.append(
                f"Ungültiges QK-Ergebnis '{parts[10]}'. Erlaubt: {list(QUALITAETSKONTROLLE.keys())}"
            )

        return validation_warnings

    def to_mb_string(self) -> str:
        """
        Convert the Meldebestaetigung back to MB Format string.

        Returns:
            The MB Format string representation
        """
        return "&".join([
            self.alphanumerischer_code,
            self.leistungsdatum_zaehler,
            self.leistungserbringer_id,
            self.datenknoten_id,
            self.meldungstyp,
            self.indikationsbereich,
            self.produktzuordnung,
            self.kostentraeger,
            self.art_der_daten,
            self.art_der_sequenzierung,
            self.qualitaetskontrolle,
        ])

    def compute_hash(self) -> str:
        """
        Compute the SHA256 hash of the MB Format string.

        Returns:
            The 64-character hexadecimal hash string
        """
        mb_string = self.to_mb_string()
        return hashlib.sha256(mb_string.encode('ascii')).hexdigest()

    def to_dict(self) -> dict:
        """
        Convert to a dictionary representation.

        Returns:
            Dictionary with all fields and their descriptive values
        """
        return {
            "alphanumerischer_code": self.alphanumerischer_code,
            "leistungsdatum": self._leistungsdatum.strftime("%Y-%m-%d") if self._leistungsdatum else None,
            "zaehler": self._zaehler,
            "leistungserbringer_id": self.leistungserbringer_id,
            "datenknoten_id": self.datenknoten_id,
            "meldungstyp": {
                "code": self.meldungstyp,
                "bezeichnung": MELDUNGSTYP.get(self.meldungstyp, "Unbekannt"),
            },
            "indikationsbereich": {
                "code": self.indikationsbereich,
                "bezeichnung": INDIKATIONSBEREICH.get(self.indikationsbereich, "Unbekannt"),
            },
            "produktzuordnung": {
                "code": self.produktzuordnung,
                "bezeichnung": PRODUKTZUORDNUNG.get(self.produktzuordnung, "Unbekannt"),
            },
            "kostentraeger": {
                "code": self.kostentraeger,
                "bezeichnung": KOSTENTRAEGER.get(self.kostentraeger, "Unbekannt"),
            },
            "art_der_daten": {
                "code": self.art_der_daten,
                "bezeichnung": ART_DER_DATEN.get(self.art_der_daten, "Unbekannt"),
            },
            "art_der_sequenzierung": {
                "code": self.art_der_sequenzierung,
                "bezeichnung": ART_DER_SEQUENZIERUNG.get(self.art_der_sequenzierung, "Unbekannt"),
            },
            "qualitaetskontrolle": {
                "code": self.qualitaetskontrolle,
                "bezeichnung": QUALITAETSKONTROLLE.get(self.qualitaetskontrolle, "Unbekannt"),
            },
            "mb_string": self.to_mb_string(),
            "hash": self.compute_hash(),
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert to JSON format.

        Args:
            indent: Number of spaces for JSON indentation (default: 2)

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def __repr__(self) -> str:
        """
        Return a clear text representation in German.

        Returns:
            Human-readable German text description
        """
        lines = [
            "═" * 60,
            "MELDEBESTÄTIGUNG (MV GenomSeq)",
            "═" * 60,
            "",
            f"Alphanumerischer Code:    {self.alphanumerischer_code}",
        ]

        if self._leistungsdatum:
            lines.append(f"Leistungsdatum:           {self._leistungsdatum.strftime('%d.%m.%Y')}")
            lines.append(f"Zähler:                   {self._zaehler:03d}")
        else:
            lines.append(f"Leistungsdatum+Zähler:    {self.leistungsdatum_zaehler}")

        lines.extend([
            f"Leistungserbringer-ID:    {self.leistungserbringer_id}",
            f"Datenknoten-ID:           {self.datenknoten_id}",
            "",
            f"Meldungstyp:              {MELDUNGSTYP.get(self.meldungstyp, 'Unbekannt')} ({self.meldungstyp})",
            f"Indikationsbereich:       {INDIKATIONSBEREICH.get(self.indikationsbereich, 'Unbekannt')} ({self.indikationsbereich})",
            f"Produktzuordnung:         {PRODUKTZUORDNUNG.get(self.produktzuordnung, 'Unbekannt')} ({self.produktzuordnung})",
            f"Kostenträger:             {KOSTENTRAEGER.get(self.kostentraeger, 'Unbekannt')} ({self.kostentraeger})",
            f"Art der Daten:            {ART_DER_DATEN.get(self.art_der_daten, 'Unbekannt')} ({self.art_der_daten})",
            f"Art der Sequenzierung:    {ART_DER_SEQUENZIERUNG.get(self.art_der_sequenzierung, 'Unbekannt')} ({self.art_der_sequenzierung})",
            f"Qualitätskontrolle:       {QUALITAETSKONTROLLE.get(self.qualitaetskontrolle, 'Unbekannt')} ({self.qualitaetskontrolle})",
            "",
            "─" * 60,
            f"MB-String: {self.to_mb_string()}",
            f"SHA256:    {self.compute_hash()}",
            "═" * 60,
        ])

        return "\n".join(lines)

    @property
    def warnings(self) -> list:
        """Return any validation warnings."""
        return self._warnings.copy() if self._warnings else []


def parse_mb_string(mb_string: str) -> Meldebestaetigung:
    """
    Convenience function to parse an MB Format string.

    Args:
        mb_string: The MB Format string to parse

    Returns:
        A Meldebestaetigung instance
    """
    return Meldebestaetigung.from_string(mb_string)

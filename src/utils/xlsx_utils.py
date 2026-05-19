from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence
from xml.etree import ElementTree as ET
from zipfile import ZipFile


SHEET_NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
REL_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def _column_index(cell_ref: str) -> int:
    letters = "".join(char for char in cell_ref if char.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + ord(char.upper()) - 64
    return index - 1


def _shared_strings(workbook: ZipFile) -> List[str]:
    try:
        root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return [
        "".join(text.text or "" for text in item.findall(".//a:t", SHEET_NS))
        for item in root.findall("a:si", SHEET_NS)
    ]


def _sheet_targets(workbook: ZipFile) -> Dict[str, str]:
    workbook_xml = ET.fromstring(workbook.read("xl/workbook.xml"))
    rels_xml = ET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels_xml.findall("rel:Relationship", REL_NS)
    }

    targets: Dict[str, str] = {}
    for sheet in workbook_xml.findall("a:sheets/a:sheet", SHEET_NS):
        target = rel_targets[sheet.attrib[REL_ID]]
        path = target[1:] if target.startswith("/") else f"xl/{target}"
        targets[sheet.attrib["name"]] = path
    return targets


def _cell_value(cell: ET.Element, shared_strings: Sequence[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(text.text or "" for text in cell.findall(".//a:t", SHEET_NS))

    value = cell.find("a:v", SHEET_NS)
    if value is None:
        return ""

    raw_value = value.text or ""
    if cell_type == "s":
        index = int(raw_value)
        return shared_strings[index] if index < len(shared_strings) else raw_value
    return raw_value


def load_xlsx_rows(path: Path, sheet_name: str | None = None) -> List[List[str]]:
    """Read one XLSX sheet using only the Python standard library."""
    with ZipFile(path) as workbook:
        shared_strings = _shared_strings(workbook)
        targets = _sheet_targets(workbook)
        if sheet_name is None:
            sheet_path = next(iter(targets.values()))
        else:
            try:
                sheet_path = targets[sheet_name]
            except KeyError as exc:
                available = ", ".join(targets)
                raise ValueError(f"Unknown sheet {sheet_name!r}; available sheets: {available}") from exc

        sheet = ET.fromstring(workbook.read(sheet_path))
        rows: List[List[str]] = []
        for row in sheet.findall("a:sheetData/a:row", SHEET_NS):
            values: List[str] = []
            current_index = 0
            for cell in row.findall("a:c", SHEET_NS):
                index = _column_index(cell.attrib.get("r", "A1"))
                while current_index < index:
                    values.append("")
                    current_index += 1
                values.append(_cell_value(cell, shared_strings))
                current_index += 1
            rows.append(values)
        return rows


def rows_to_dicts(rows: Sequence[Sequence[str]], header_row: int = 0) -> List[Dict[str, str]]:
    headers = [str(value).strip() for value in rows[header_row]]
    records: List[Dict[str, str]] = []
    for row in rows[header_row + 1 :]:
        if not any(str(value).strip() for value in row):
            continue
        padded = list(row) + [""] * max(0, len(headers) - len(row))
        records.append({header: str(value).strip() for header, value in zip(headers, padded)})
    return records


def find_header_row(rows: Sequence[Sequence[str]], first_column_name: str) -> int:
    for index, row in enumerate(rows):
        if row and str(row[0]).strip() == first_column_name:
            return index
    raise ValueError(f"Could not find header row starting with {first_column_name!r}")

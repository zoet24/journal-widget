#!/usr/bin/env python3
"""
Journal Converter: Converts .docx journal files to structured JSON.

Each entry is parsed into:
  - id:       randomly generated UUID
  - date:     the date following "Date:"
  - today:    text from "Today I am:" + text from "Fran/Mum/Dad/Izi:" appended at the end
  - grateful: text from "I am grateful for:"
  - stuff:    text from "Books/Films/TV/Music/Articles:"
  - quotes:   text from "Quotes:" (empty string if section not present)

Missing sections default to empty string "".

Usage:
  python convert_journal.py --input /path/to/journal/docs --output journal.json
  python convert_journal.py --input /path/to/January_2024.docx --output journal.json
"""

import os
import re
import json
import uuid
import argparse
from datetime import datetime
from pathlib import Path

try:
    import docx
except ImportError:
    print("Installing python-docx...")
    os.system("pip install python-docx --break-system-packages -q")
    import docx


# Section headers that are tracked and mapped to output fields
SECTION_HEADERS = [
    (r'today i am',                    'today'),
    (r'i am grateful for',             'grateful'),
    (r'books/films/tv/music/articles', 'stuff'),
    (r'quotes',                        'quotes'),
    (r'fran/mum/dad/izi',              'fran'),
]

# Section headers that should be silently ignored (content discarded)
IGNORED_HEADERS = [
    r'exercise',
]

ALL_HEADERS = SECTION_HEADERS + [(h, '__ignore__') for h in IGNORED_HEADERS]


def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)
    return '\n'.join(para.text for para in doc.paragraphs)


def parse_date(date_str):
    formats = [
        '%b %d, %Y',  # Mar 4, 2026
        '%B %d, %Y',  # March 4, 2026
        '%d/%m/%Y',   # 04/03/2026
        '%m/%d/%Y',   # 03/04/2026
        '%Y-%m-%d',   # 2026-03-04
        '%d %B %Y',   # 4 March 2026
        '%d %b %Y',   # 4 Mar 2026
    ]
    date_str = date_str.strip()
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return date_str


def split_into_entries(text):
    """Split on lines beginning with 'Date:' (value on same line)."""
    parts = re.split(r'(?=^Date:\s+\S)', text, flags=re.MULTILINE | re.IGNORECASE)
    return [p.strip() for p in parts if p.strip() and re.match(r'^Date:', p.strip(), re.IGNORECASE)]


def parse_entry(entry_text):
    fields = {
        'date':     '',
        'today':    '',
        'grateful': '',
        'stuff':    '',
        'quotes':   '',
        'fran':     '',
    }

    # Extract date from first line ("Date: Mar 4, 2026")
    first_line = entry_text.split('\n')[0]
    date_match = re.match(r'^Date:\s+(.+)$', first_line.strip(), re.IGNORECASE)
    if not date_match:
        return None
    fields['date'] = parse_date(date_match.group(1))

    # Build regex matching all tracked + ignored headers (alone on a line)
    header_re = re.compile(
        r'^(' + '|'.join(h for h, _ in ALL_HEADERS) + r')\s*:\s*$',
        re.IGNORECASE | re.MULTILINE
    )

    last_field = None
    last_end = 0

    for match in header_re.finditer(entry_text):
        # Save previous section's content (unless it's ignored)
        if last_field is not None and last_field != '__ignore__':
            fields[last_field] = entry_text[last_end:match.start()].strip()

        # Identify which field this header maps to
        header_text = match.group(1).lower()
        last_field = next(
            (field for pattern, field in ALL_HEADERS
             if re.fullmatch(pattern, header_text, re.IGNORECASE)),
            None
        )
        last_end = match.end()

    # Save the final section
    if last_field is not None and last_field != '__ignore__':
        fields[last_field] = entry_text[last_end:].strip()

    # Append Fran/Mum/Dad/Izi to today
    today_text = fields['today']
    if fields['fran']:
        today_text = (today_text + '\n\n' + fields['fran']).strip() if today_text else fields['fran']

    return {
        'id':       str(uuid.uuid4()),
        'date':     fields['date'],
        'today':    today_text,
        'grateful': fields['grateful'],
        'stuff':    fields['stuff'],
        'quotes':   fields['quotes'],
    }


def process_file(filepath):
    print(f"  Processing: {Path(filepath).name}")
    try:
        text = extract_text_from_docx(filepath)
    except Exception as e:
        print(f"  Could not read {filepath}: {e}")
        return []

    raw_entries = split_into_entries(text)
    print(f"    Found {len(raw_entries)} entries")

    parsed = []
    for raw in raw_entries:
        entry = parse_entry(raw)
        if entry:
            parsed.append(entry)
        else:
            print(f"    Skipped an entry (no parseable date)")
    return parsed


def convert_journal(input_path, output_path):
    input_p = Path(input_path)
    all_entries = []

    if input_p.is_dir():
        docx_files = sorted(input_p.glob('**/*.docx'))
        if not docx_files:
            print(f"No .docx files found in {input_path}")
            return
        print(f"Found {len(docx_files)} .docx files\n")
        for f in docx_files:
            all_entries.extend(process_file(str(f)))
    elif input_p.is_file() and input_p.suffix.lower() == '.docx':
        all_entries.extend(process_file(str(input_p)))
    else:
        print(f"Error: {input_path} is not a .docx file or directory")
        return

    all_entries.sort(key=lambda e: e['date'])

    output_p = Path(output_path)
    output_p.parent.mkdir(parents=True, exist_ok=True)
    with open(output_p, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Converted {len(all_entries)} entries → {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert journal .docx files to JSON')
    parser.add_argument('--input',  '-i', required=True)
    parser.add_argument('--output', '-o', default='journal.json')
    args = parser.parse_args()
    convert_journal(args.input, args.output)
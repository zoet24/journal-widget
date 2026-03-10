# Journal Widget

A macOS desktop widget built with [Übersicht](https://tracesof.net/uebersicht/) that surfaces three things from your journal every day:

- 👋 **Today** — a daily writing prompt to get you thinking
- 🗓️ **On this day** — a random paragraph from a past journal entry
- 💚 **Grateful for** — a random gratitude note from a past entry

All picks are seeded to the current date, so the widget shows the same content all day and refreshes with something new each morning.

---

## Project structure

```
journal-widget/
├── journal-widget.jsx   # Übersicht widget
├── widget-preview.html  # Local browser preview for iterating on design
├── convertJournal.py    # Script to convert .docx journal files to JSON
├── prompts.json         # Array of daily writing prompts
├── journals/            # .docx journal files (gitignored)
└── journal.json         # Generated journal data (gitignored)
```

---

## Setup

### 1. Install dependencies

- [Übersicht](https://tracesof.net/uebersicht/) — for running the desktop widget
- Python 3 with `python-docx`:

```bash
pip3 install python-docx
```

### 2. Convert your journal docs

Place your `.docx` journal files in the `journals/` folder, then run:

```bash
python3 /Users/zoethexton/Desktop/Zoepix/Code/journal-widget/convertJournal.py \
  --input "/Users/zoethexton/Desktop/Zoepix/Code/journal-widget/journals/" \
  --output /Users/zoethexton/Desktop/Zoepix/Code/journal-widget/journal.json
```

Re-run this any time you add new journal docs — it will regenerate `journal.json` from scratch.

Each `.docx` file should contain journal entries separated by `Date:` lines, with sections for `Today I am:`, `I am grateful for:`, `Books/Films/TV/Music/Articles:`, `Quotes:`, and `Fran/Mum/Dad/Izi:`.

### 3. Install the widget

Copy `journal-widget.jsx` into your Übersicht widgets folder:

```
~/Library/Application Support/Übersicht/widgets/
```

You can open this folder quickly via the Übersicht menu bar icon → **Open Widgets Folder**. The widget will appear on your desktop automatically.

### 4. Customise prompts

Edit `prompts.json` to add, remove, or rewrite the daily writing prompts — it's just an array of strings.

---

## Local preview

To iterate on the widget design in a browser before updating the `.jsx`:

```bash
cd /Users/zoethexton/Desktop/Zoepix/Code/journal-widget
python3 -m http.server 8000
```

Then open [http://localhost:8000/widget-preview.html](http://localhost:8000/widget-preview.html).

The preview includes **← Prev**, **Next →**, and **🔀 Shuffle** controls to cycle through entries and see how different content lengths look.

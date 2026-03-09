// Journal Widget for Übersicht
// Place this file in ~/Library/Application Support/Übersicht/widgets/

export const command = `cat /Users/zoethexton/Desktop/Zoepix/Code/journal-widget/journal.json`;

export const refreshFrequency = 1000 * 60 * 60; // refresh every hour

export const className = `
  top: 24px;
  left: 24px;
  width: 340px;
  font-family: -apple-system, 'Helvetica Neue', sans-serif;

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  .card {
    width: 340px;
    max-height: calc(100vh - 48px);
    overflow-y: auto;
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 16px;
    padding: 20px 22px 22px;
    box-shadow:
      0 8px 32px rgba(0, 0, 0, 0.18),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
    animation: fadeIn 0.6s ease;
  }

  .card::-webkit-scrollbar {
    width: 4px;
  }

  .card::-webkit-scrollbar-track {
    background: transparent;
  }

  .card::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
  }

  .card::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.35);
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-6px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 12px;
  }

  .icon {
    font-size: 13px;
    line-height: 1;
  }

  .label {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255, 255, 255, 0.5);
  }

  .date {
    font-size: 12px;
    font-weight: 400;
    color: rgba(255, 255, 255, 0.35);
    margin-left: auto;
    letter-spacing: 0.04em;
  }

  .divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.12);
    margin-bottom: 14px;
  }

  .section-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.08);
    margin: 18px 0;
  }

  .today-para {
    font-size: 14px;
    line-height: 1.65;
    color: rgba(255, 255, 255, 0.88);
    word-break: break-word;
    margin: 0 0 0.75em 0;
  }

  .today-para:last-child {
    margin-bottom: 0;
  }

  .grateful-text {
    font-size: 14px;
    line-height: 1.65;
    color: rgba(255, 255, 255, 0.88);
    word-break: break-word;
  }

  .error {
    font-size: 11px;
    color: rgba(255, 120, 120, 0.8);
  }
`;

// ── Seeded random helpers ─────────────────────────────────────────────────────
function seededRandom(seed) {
  let x = Math.sin(seed + 1) * 10000;
  return x - Math.floor(x);
}

function seededRandom2(seed) {
  let x = Math.sin(seed + 99) * 10000;
  return x - Math.floor(x);
}

function getTodaysSeed() {
  const now = new Date();
  return now.getFullYear() * 10000 + (now.getMonth() + 1) * 100 + now.getDate();
}

function formatDate(isoDate) {
  if (!isoDate) return "";
  const [year, month, day] = isoDate.split("-").map(Number);
  const d = new Date(year, month - 1, day);
  return d.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function pickRandomParagraph(text, seed) {
  const paras = (text || "")
    .split(/\n+/)
    .map((p) => p.trim())
    .filter((p) => p.length > 0);
  if (paras.length === 0) return "";
  return paras[Math.floor(seededRandom2(seed) * paras.length)];
}

function pickEntries(entries) {
  const seed = getTodaysSeed();

  const withGrateful = entries.filter(
    (e) => e.grateful && e.grateful.trim().length > 0
  );
  const gratefulEntry =
    withGrateful[Math.floor(seededRandom(seed) * withGrateful.length)];

  const withToday = entries.filter(
    (e) => e.today && e.today.trim().length > 0 && e.id !== gratefulEntry?.id
  );
  const todayEntry =
    withToday[Math.floor(seededRandom2(seed) * withToday.length)];

  return { gratefulEntry, todayEntry, seed };
}

// ── Render ────────────────────────────────────────────────────────────────────
export const render = ({ output, error }) => {
  if (error) {
    return (
      <div className="card">
        <p className="error">Could not load journal.json</p>
      </div>
    );
  }

  let entries = [];
  try {
    entries = JSON.parse(output);
  } catch (e) {
    return (
      <div className="card">
        <p className="error">Could not parse journal.json</p>
      </div>
    );
  }

  if (!entries.length) {
    return (
      <div className="card">
        <p className="error">No entries found.</p>
      </div>
    );
  }

  const { gratefulEntry, todayEntry, seed } = pickEntries(entries);
  const selectedPara = todayEntry
    ? pickRandomParagraph(todayEntry.today, seed)
    : "";

  return (
    <div className="card">
      <div className="section-header">
        <span className="icon">📖</span>
        <span className="label">On this day</span>
        <span className="date">
          {todayEntry ? formatDate(todayEntry.date) : ""}
        </span>
      </div>
      <div className="divider" />
      <p className="today-para">{selectedPara || "(no entry text)"}</p>

      <div className="section-divider" />

      <div className="section-header">
        <span className="icon">🤍</span>
        <span className="label">Grateful for</span>
        <span className="date">
          {gratefulEntry ? formatDate(gratefulEntry.date) : ""}
        </span>
      </div>
      <div className="divider" />
      <p className="grateful-text">
        {gratefulEntry?.grateful || "(no grateful text)"}
      </p>
    </div>
  );
};

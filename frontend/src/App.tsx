import { useEffect, useMemo, useState } from "react";
import "./App.css";

type Category = "MUST_SEE" | "IMPORTANT" | "UNSURE" | "LOW_PRIORITY" | "TRASH";

interface Item {
  id: string;
  sender: string;
  subject: string;
  received: string;
  preview: string;
  reason: string;
  source: "model" | "my label";
}

interface Payload {
  total: number;
  counts: Record<Category, number>;
  categories: Record<Category, Item[]>;
}

const API = "http://127.0.0.1:8000/api/emails";
const PAGE = 50;

// Order = priority.
const NAV: { key: Category; title: string; hint: string }[] = [
  { key: "MUST_SEE", title: "Must see", hint: "Needs you soon: deadlines, security alerts, legal." },
  { key: "IMPORTANT", title: "Important", hint: "Worth reading, not urgent: replies, bills, rejections." },
  { key: "UNSURE", title: "Unsure", hint: "The model could not decide. Check these yourself." },
  { key: "LOW_PRIORITY", title: "Low priority", hint: "Receipts, codes and notices. Findable later." },
  { key: "TRASH", title: "Trash", hint: "Marketing, digests and noise. Nothing is deleted." },
];

// NOTE: everything from an email is rendered as plain text through JSX.
// Never use dangerouslySetInnerHTML: subjects, bodies and the model's
// "reason" are attacker-controlled.

function senderName(from: string): string {
  const name = from.replace(/<[^>]*>/g, "").replace(/"/g, "").trim();
  return name || from;
}

function shortDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const sameYear = d.getFullYear() === new Date().getFullYear();
  return d.toLocaleDateString(undefined, sameYear ? { month: "short", day: "numeric" } : { month: "short", day: "numeric", year: "numeric" });
}

function Row({ item, tag }: { item: Item; tag?: Category }) {
  const [open, setOpen] = useState(false);
  return (
    <li className={`row ${open ? "open" : ""}`}>
      <button className="row-head" onClick={() => setOpen(!open)} aria-expanded={open}>
        <span className="from">{senderName(item.sender)}</span>
        <span className="mid">
          {tag && <span className={`tag tag-${tag}`}>{NAV.find((n) => n.key === tag)?.title}</span>}
          <span className="subject">{item.subject || "(no subject)"}</span>
          <span className="snippet"> — {item.preview}</span>
        </span>
        <span className="when">{shortDate(item.received)}</span>
      </button>
      {open && (
        <div className="detail">
          <p className="full-from">{item.sender}</p>
          {item.preview && <p className="body">{item.preview}</p>}
          {item.reason && (
            <p className="why">
              <strong>Why this category:</strong> {item.reason}
            </p>
          )}
          <div className="actions">
            <span className={`source ${item.source === "model" ? "model" : "hand"}`}>
              {item.source === "model" ? "Model decision" : "Your label"}
            </span>
            <a href={`https://mail.google.com/mail/u/0/#all/${item.id}`} target="_blank" rel="noopener noreferrer">
              Open in Gmail ↗
            </a>
          </div>
        </div>
      )}
    </li>
  );
}

function List({ rows, showTags }: { rows: { item: Item; cat: Category }[]; showTags: boolean }) {
  const [shown, setShown] = useState(PAGE);
  if (rows.length === 0) return <p className="empty">Nothing here.</p>;
  return (
    <>
      <ul className="list">
        {rows.slice(0, shown).map(({ item, cat }) => (
          <Row key={item.id} item={item} tag={showTags ? cat : undefined} />
        ))}
      </ul>
      {rows.length > shown && (
        <button className="more" onClick={() => setShown(shown + PAGE)}>
          Show more ({rows.length - shown} left)
        </button>
      )}
    </>
  );
}

export default function App() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [active, setActive] = useState<Category | null>(null);
  const [query, setQuery] = useState("");

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setData((await res.json()) as Payload);
    } catch (e) {
      setError(e instanceof Error ? e.message : "request failed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const current: Category = active ?? NAV.find((n) => data && data.counts[n.key] > 0)?.key ?? "MUST_SEE";
  const q = query.trim().toLowerCase();

  const rows = useMemo(() => {
    if (!data) return [];
    const source = q ? NAV.map((n) => n.key) : [current];
    return source.flatMap((cat) =>
      data.categories[cat]
        .filter((i) => !q || `${i.sender} ${i.subject} ${i.preview}`.toLowerCase().includes(q))
        .map((item) => ({ item, cat })),
    );
  }, [data, current, q]);

  const meta = NAV.find((n) => n.key === current);

  return (
    <div className="app">
      <aside className="side">
        <div className="brand">
          <span className="logo">✉</span> Triage
        </div>
        <nav>
          {NAV.map((n) => (
            <button
              key={n.key}
              className={`nav ${!q && current === n.key ? "active" : ""}`}
              onClick={() => {
                setActive(n.key);
                setQuery("");
              }}
            >
              <span className={`dot dot-${n.key}`} />
              <span className="nav-title">{n.title}</span>
              <span className="nav-count">{data ? data.counts[n.key] : "–"}</span>
            </button>
          ))}
        </nav>
        <div className="side-foot">
          <button className="refresh" onClick={load} disabled={loading}>
            {loading ? "Loading…" : "Refresh"}
          </button>
          <p>Triage helper, not a filter. Everything is still in Gmail. Not yet tested on much real person mail.</p>
        </div>
      </aside>

      <main className="main">
        <header className="bar">
          <div>
            <h1>{q ? "Search results" : meta?.title}</h1>
            <p className="hint">{q ? `${rows.length} matches across all categories` : meta?.hint}</p>
          </div>
          <input
            className="search"
            type="search"
            placeholder="Search sender, subject, text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </header>

        {error && <p className="error">Could not reach the API ({error}). Is the backend running on port 8000?</p>}
        {!data && !error && <p className="empty">Loading…</p>}
        {data && <List key={`${current}|${q}`} rows={rows} showTags={q.length > 0} />}
      </main>
    </div>
  );
}

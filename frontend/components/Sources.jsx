// Shows which pages of the PDF the answer came from.

export default function Sources({ sources }) {
  if (!sources || sources.length === 0) return null;

  // Group passages by page, keeping the most relevant page first
  const groups = new Map();
  for (const source of sources) {
    const key = `${source.document}|${source.page}`;
    if (!groups.has(key)) {
      groups.set(key, { key, document: source.document, page: source.page, snippets: [] });
    }
    groups.get(key).snippets.push(source.snippet);
  }
  const pages = [...groups.values()];

  return (
    <div className="mt-2.5">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-subtle">Sources</p>

      <div className="mt-1.5 flex flex-wrap gap-1.5">
        {pages.map((p) => (
          <span
            key={p.key}
            className="rounded-full border border-accent/40 bg-accent/10 px-2.5 py-0.5 text-xs font-medium text-accent"
          >
            Page {p.page}
          </span>
        ))}
      </div>

      <details className="mt-2 text-xs text-muted">
        <summary className="cursor-pointer select-none py-1 text-subtle hover:text-fg">
          View passages
        </summary>
        <ul className="mt-2 space-y-2">
          {pages.flatMap((p) =>
            p.snippets.map((snippet, index) => (
              <li key={`${p.key}-${index}`} className="rounded-xl border border-line bg-field p-2.5">
                <span className="font-medium text-fg">
                  {p.document} - page {p.page}
                </span>
                <p className="mt-1 whitespace-pre-wrap break-words">{snippet}</p>
              </li>
            ))
          )}
        </ul>
      </details>
    </div>
  );
}

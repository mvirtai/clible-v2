import type { Components } from 'react-markdown';

export function markdownComponents(options: {
  invert: boolean;
  /** Larger ## / ### hierarchy for AI Insights (Reader panel). */
  insightLayout?: boolean;
  /** Dark analytics card: ## section titles larger than body **bold**. */
  toneLayout?: boolean;
}): Components {
  const { invert, insightLayout, toneLayout } = options;
  const body = invert ? 'text-gray-200' : 'text-[var(--text)]';
  const strongCls = invert ? 'font-semibold text-white' : 'font-semibold text-[var(--text)]';
  const codeBg = invert ? 'bg-gray-800 text-gray-100' : 'bg-[var(--surface)] text-[var(--text)]';
  const quoteBorder = invert ? 'border-gray-600' : 'border-[var(--accent)]';

  const headings: Pick<Components, 'h1' | 'h2' | 'h3'> =
    insightLayout && !invert
      ? {
        h1: ({ children }) => (
          <h1 className="mb-4 mt-1 text-3xl font-bold tracking-tight text-[var(--text)] first:mt-0">
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 className="mt-10 border-b border-[var(--border-soft)] pb-2 text-2xl font-bold text-[var(--text)] first:mt-2 mb-3">
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 className="mb-2 mt-6 text-lg font-semibold text-[var(--text)]">
            {children}
          </h3>
        ),
      }
      : toneLayout && invert
        ? {
          h1: ({ children }) => (
            <h1 className="mb-3 mt-1 text-2xl font-bold tracking-tight text-gray-100 first:mt-0">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="mb-3 mt-8 border-b border-gray-600 pb-2 text-xl font-bold text-gray-100 first:mt-3">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="mb-2 mt-5 text-lg font-semibold text-gray-100">
              {children}
            </h3>
          ),
        }
        : {
          h1: ({ children }) => (
            <h3 className={`mb-2 mt-4 text-lg font-semibold ${strongCls}`}>
              {children}
            </h3>
          ),
          h2: ({ children }) => (
            <h3 className={`mb-2 mt-3 text-base font-semibold ${strongCls}`}>
              {children}
            </h3>
          ),
          h3: ({ children }) => (
            <h4 className={`mb-1 mt-2 text-sm font-semibold ${strongCls}`}>
              {children}
            </h4>
          ),
        };

  return {
    ...headings,
    p: ({ children }) => (
      <p
        className={`mb-3 last:mb-0 leading-relaxed ${body} ${toneLayout && invert ? 'text-base' : ''
          }`}
      >
        {children}
      </p>
    ),
    strong: ({ children }) => (
      <strong
        className={
          toneLayout && invert
            ? 'font-semibold text-white'
            : strongCls
        }
      >
        {children}
      </strong>
    ),
    em: ({ children }) => <em className="italic">{children}</em>,
    ul: ({ children }) => (
      <ul className={`mb-3 list-disc text-[var(--text)] space-y-1 pl-5 ${body}`}>{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className={`mb-3 list-decimal text-[var(--text)] space-y-1 pl-5 ${body}`}>{children}</ol>
    ),
    li: ({ children }) => <li className="leading-relaxed">{children}</li>,
    table: ({ children }) => (
      <div className="mb-4 overflow-x-auto">
        <table className="w-full border-collapse text-sm text-[var(--text)]">{children}</table>
      </div>
    ),
    thead: ({ children }) => (
      <thead className={invert ? 'bg-gray-800/70' : 'bg-[var(--surface-2)]'}>{children}</thead>
    ),
    tbody: ({ children }) => <tbody>{children}</tbody>,
    tr: ({ children }) => (
      <tr className={invert ? 'border-b border-gray-700' : 'border-b border-[var(--border-soft)]'}>
        {children}
      </tr>
    ),
    th: ({ children }) => (
      <th
        className={`px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide ${invert ? 'text-gray-200 border-b border-gray-600' : 'text-[var(--muted)] border-b border-[var(--border)]'
          }`}
      >
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className={`px-3 py-2 align-top ${invert ? 'text-gray-200' : 'text-[var(--text)]'}`}>
        {children}
      </td>
    ),
    code: ({ children }) => (
      <code className={`rounded px-1 py-0.5 text-[var(--text)] font-mono text-[0.9em] ${codeBg}`}>
        {children}
      </code>
    ),
    blockquote: ({ children }) => (
      <blockquote className={`my-3 border-l-4 text-[var(--text)] pl-3 opacity-90 ${quoteBorder}`}>
        {children}
      </blockquote>
    ),
    hr: () => (
      <hr
        className={`my-4 border-0 border-t ${invert ? 'border-gray-700' : 'border-[var(--border-soft)]'}`}
      />
    ),
  };
}

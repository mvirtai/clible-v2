import type { Components } from 'react-markdown';

export function markdownComponents(options: {
  invert: boolean;
  /** Larger ## / ### hierarchy for AI Insights (Reader panel). */
  insightLayout?: boolean;
  /** Dark analytics card: ## section titles larger than body **bold**. */
  toneLayout?: boolean;
}): Components {
  const { invert, insightLayout, toneLayout } = options;
  const body = invert ? 'text-gray-200' : 'text-[#333]';
  const strongCls = invert ? 'font-semibold text-white' : 'font-semibold text-[#1A1A1A]';
  const codeBg = invert ? 'bg-gray-800 text-gray-100' : 'bg-[#F0F0F0] text-[#1A1A1A]';
  const quoteBorder = invert ? 'border-gray-600' : 'border-[#D4A373]';

  const headings: Pick<Components, 'h1' | 'h2' | 'h3'> =
    insightLayout && !invert
      ? {
          h1: ({ children }) => (
            <h1 className="mb-4 mt-1 text-3xl font-bold tracking-tight text-[#1A1A1A] first:mt-0">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="mt-10 border-b border-[#E8E4DC] pb-2 text-2xl font-bold text-[#1A1A1A] first:mt-2 mb-3">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="mb-2 mt-6 text-lg font-semibold text-[#1A1A1A]">
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
        className={`mb-3 last:mb-0 leading-relaxed ${body} ${
          toneLayout && invert ? 'text-base' : ''
        }`}
      >
        {children}
      </p>
    ),
    strong: ({ children }) => (
      <strong
        className={
          toneLayout && invert
            ? 'font-semibold text-gray-200'
            : strongCls
        }
      >
        {children}
      </strong>
    ),
    em: ({ children }) => <em className="italic">{children}</em>,
    ul: ({ children }) => (
      <ul className={`mb-3 list-disc space-y-1 pl-5 ${body}`}>{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className={`mb-3 list-decimal space-y-1 pl-5 ${body}`}>{children}</ol>
    ),
    li: ({ children }) => <li className="leading-relaxed">{children}</li>,
    code: ({ children }) => (
      <code className={`rounded px-1 py-0.5 font-mono text-[0.9em] ${codeBg}`}>
        {children}
      </code>
    ),
    blockquote: ({ children }) => (
      <blockquote className={`my-3 border-l-4 pl-3 opacity-90 ${quoteBorder}`}>
        {children}
      </blockquote>
    ),
    hr: () => (
      <hr
        className={`my-4 border-0 border-t ${invert ? 'border-gray-600' : 'border-[#E5E5E5]'}`}
      />
    ),
  };
}

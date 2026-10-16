import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Shows the AI's answer with simple formatting (bold, lists, code, tables).
// Raw HTML inside the answer is NOT allowed: react-markdown shows it as plain text,
// so a PDF cannot sneak scripts or images into the page.

const components = {
  p: ({ children }) => <p className="mt-2 first:mt-0">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold text-fg">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  ul: ({ children }) => <ul className="mt-2 list-disc space-y-1 pl-5 first:mt-0">{children}</ul>,
  ol: ({ children }) => <ol className="mt-2 list-decimal space-y-1 pl-5 first:mt-0">{children}</ol>,
  li: ({ children }) => <li className="pl-0.5">{children}</li>,
  h1: ({ children }) => <p className="mt-3 text-base font-semibold text-fg first:mt-0">{children}</p>,
  h2: ({ children }) => <p className="mt-3 text-base font-semibold text-fg first:mt-0">{children}</p>,
  h3: ({ children }) => <p className="mt-3 font-semibold text-fg first:mt-0">{children}</p>,
  h4: ({ children }) => <p className="mt-3 font-semibold text-fg first:mt-0">{children}</p>,
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer nofollow" className="text-accent underline">
      {children}
    </a>
  ),
  blockquote: ({ children }) => (
    <blockquote className="mt-2 border-l-2 border-line-strong pl-3 text-muted">{children}</blockquote>
  ),
  hr: () => <hr className="my-3 border-line" />,
  code: ({ children }) => (
    <code className="rounded bg-hover px-1 py-0.5 font-mono text-[0.85em]">{children}</code>
  ),
  pre: ({ children }) => (
    <pre className="mt-2 overflow-x-auto rounded-xl border border-line bg-field p-3 text-xs [&_code]:bg-transparent [&_code]:p-0">
      {children}
    </pre>
  ),
  table: ({ children }) => (
    <div className="mt-2 overflow-x-auto">
      <table className="w-full border-collapse text-left text-xs">{children}</table>
    </div>
  ),
  th: ({ children }) => (
    <th className="border border-line bg-field px-2 py-1 font-semibold text-fg">{children}</th>
  ),
  td: ({ children }) => <td className="border border-line px-2 py-1">{children}</td>,
};

export default function Markdown({ children }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {children}
    </ReactMarkdown>
  );
}

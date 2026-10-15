import Sources from "./Sources";

// One chat message: a user question or an assistant answer.
// message = { role, content, found?, sources?, isError? }

export default function Message({ message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="bg-accent-gradient max-w-[88%] whitespace-pre-wrap break-words rounded-2xl rounded-br-md px-4 py-2.5 text-sm font-medium text-on-accent sm:max-w-[80%]">
          {message.content}
        </div>
      </div>
    );
  }

  const isError = Boolean(message.isError);
  const notFound = message.found === false;

  let bubbleStyle = "border border-line bg-bubble text-fg";
  if (isError) {
    bubbleStyle =
      "border border-red-500/40 bg-red-500/10 text-red-800 dark:border-red-400/30 dark:text-red-200";
  } else if (notFound) {
    bubbleStyle =
      "border border-amber-500/40 bg-amber-500/10 text-amber-900 dark:border-amber-400/30 dark:bg-amber-400/10 dark:text-amber-200";
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[94%] sm:max-w-[85%]">
        <div
          className={`whitespace-pre-wrap break-words rounded-2xl rounded-bl-md px-4 py-2.5 text-sm leading-relaxed ${bubbleStyle}`}
        >
          {isError && <span className="font-semibold">Error: </span>}
          {message.content}
        </div>

        {!isError && message.found && <Sources sources={message.sources} />}
      </div>
    </div>
  );
}

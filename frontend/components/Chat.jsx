"use client";

import { useEffect, useRef, useState } from "react";
import { useSlowFlag } from "@/lib/hooks";
import Message from "./Message";

export default function Chat({ messages, loading, hasDocument, onSend, onClear }) {
  const [input, setInput] = useState("");
  const listRef = useRef(null);
  const inputRef = useRef(null);
  const slow = useSlowFlag(loading);

  // When a document becomes ready, put the cursor in the question box
  useEffect(() => {
    if (hasDocument) inputRef.current?.focus();
  }, [hasDocument]);

  // Keep the newest message in view (scroll only the chat box, not the page)
  useEffect(() => {
    const list = listRef.current;
    if (list) list.scrollTop = list.scrollHeight;
  }, [messages, loading]);

  function handleSubmit(event) {
    event.preventDefault();
    const question = input.trim();
    if (!question || loading || !hasDocument) return;
    setInput("");
    onSend(question);
  }

  const canClear = hasDocument || messages.length > 0;

  return (
    <section className="surface flex h-[72dvh] max-h-[46rem] min-h-[26rem] flex-col overflow-hidden lg:h-[calc(100dvh-11.5rem)] lg:max-h-none lg:min-h-[32rem]">
      <div className="flex items-center justify-between gap-3 border-b border-white/10 px-4 py-3 sm:px-5">
        <h2 className="text-base font-semibold text-white">2. Ask questions</h2>
        <button type="button" onClick={onClear} disabled={!canClear} className="btn-ghost !px-3 !py-1.5">
          Clear
        </button>
      </div>

      <div ref={listRef} className="min-h-0 flex-1 space-y-4 overflow-y-auto px-4 py-4 sm:px-5">
        {messages.length === 0 && !loading && (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
            <div className="bg-accent-gradient flex h-12 w-12 items-center justify-center rounded-2xl text-black">
              <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z" />
              </svg>
            </div>
            <p className="max-w-xs text-sm text-zinc-400">
              {hasDocument
                ? "Your PDF is ready. Ask a question about it."
                : "Upload a PDF to start chatting."}
            </p>
          </div>
        )}

        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}

        {loading && (
          <div className="flex justify-start" role="status" aria-label="The assistant is thinking">
            <div className="flex items-center gap-3 rounded-2xl rounded-bl-md border border-white/10 bg-white/[0.06] px-4 py-3">
              <div className="flex items-center gap-1.5">
                {[0, 150, 300].map((delay) => (
                  <span
                    key={delay}
                    className="h-2 w-2 animate-bounce rounded-full bg-accent"
                    style={{ animationDelay: `${delay}ms` }}
                  />
                ))}
              </div>
              {slow && (
                <span className="text-xs text-zinc-500">
                  Taking longer than usual - the server may be waking up...
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex gap-2 border-t border-white/10 p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] sm:p-4"
      >
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={!hasDocument}
          maxLength={1000}
          placeholder={hasDocument ? "Ask a question about your PDF..." : "Upload a PDF first"}
          className="min-w-0 flex-1 rounded-xl border border-white/10 bg-white/5 px-3.5 py-2.5 text-base text-zinc-100 outline-none placeholder:text-zinc-500 focus:border-accent focus:ring-2 focus:ring-accent/30 disabled:cursor-not-allowed disabled:opacity-50 sm:text-sm"
        />
        <button
          type="submit"
          disabled={!hasDocument || loading || input.trim() === ""}
          className="btn-primary"
        >
          Send
        </button>
      </form>
    </section>
  );
}

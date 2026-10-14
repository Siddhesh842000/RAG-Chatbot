"use client";

import { useState } from "react";
import Chat from "@/components/Chat";
import HowItWorks from "@/components/HowItWorks";
import ThemePicker from "@/components/ThemePicker";
import Upload from "@/components/Upload";
import { askQuestion, clearDocument, uploadPdf } from "@/lib/api";
import { getSessionId } from "@/lib/session";

const makeId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

export default function Home() {
  const [doc, setDoc] = useState(null); // { filename, pages, chunks }
  const [upload, setUpload] = useState({ status: "idle", message: "" });
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);
  const [resetKey, setResetKey] = useState(0); // changing it resets the Upload box

  async function handleUpload(file) {
    setUpload({ status: "uploading", message: "Uploading and processing your PDF..." });
    try {
      const result = await uploadPdf(file, getSessionId());
      setDoc({ filename: result.filename, pages: result.pages, chunks: result.chunks });
      setMessages([]);
      setUpload({ status: "success", message: result.message });
    } catch (error) {
      setUpload({ status: "error", message: error.message });
    }
  }

  async function handleAsk(question) {
    setMessages((prev) => [...prev, { id: makeId(), role: "user", content: question }]);
    setAsking(true);
    try {
      const result = await askQuestion(question, getSessionId());
      setMessages((prev) => [
        ...prev,
        {
          id: makeId(),
          role: "assistant",
          content: result.answer,
          found: result.found,
          sources: result.sources,
        },
      ]);
    } catch (error) {
      let text = error.message;

      // 404 means the server has no document for us. This happens when the
      // free server restarts, because it keeps documents in memory only.
      if (error.status === 404) {
        text =
          "The server no longer has your document (it may have restarted). Please upload the PDF again.";
        setDoc(null);
        setUpload({ status: "idle", message: "" });
      }

      setMessages((prev) => [
        ...prev,
        { id: makeId(), role: "assistant", content: text, isError: true },
      ]);
    } finally {
      setAsking(false);
    }
  }

  async function handleClear() {
    try {
      await clearDocument(getSessionId());
    } catch {
      // Even if the server call fails, we still reset the screen
    }
    setDoc(null);
    setMessages([]);
    setUpload({ status: "idle", message: "" });
    setResetKey((key) => key + 1);
  }

  return (
    <div className="mx-auto w-full max-w-6xl px-4 pb-8 pt-6 sm:px-6 lg:px-8 lg:pt-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-accent">
            PDF question answering
          </p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">
            <span className="text-gradient">RAG Chatbot</span>
          </h1>
          <p className="mt-2 max-w-xl text-sm text-zinc-400">
            Upload a PDF and ask questions about it. Answers come only from your document and show
            the source pages.
          </p>
        </div>
        <ThemePicker />
      </header>

      <main className="mt-6 grid gap-4 lg:grid-cols-[22rem_minmax(0,1fr)] lg:items-start">
        <div className="flex flex-col gap-4 lg:sticky lg:top-6">
          <Upload
            key={resetKey}
            onUpload={handleUpload}
            status={upload.status}
            message={upload.message}
            doc={doc}
          />
          <HowItWorks />
        </div>

        <Chat
          messages={messages}
          loading={asking}
          hasDocument={Boolean(doc)}
          onSend={handleAsk}
          onClear={handleClear}
        />
      </main>

      <footer className="mt-8 text-center text-xs text-zinc-600">
        Built with Next.js, FastAPI, FAISS and Groq
      </footer>
    </div>
  );
}

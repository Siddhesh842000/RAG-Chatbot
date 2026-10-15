"use client";

import { useRef, useState } from "react";
import { useSlowFlag } from "@/lib/hooks";

const MAX_FILE_MB = 10; // same limit as the backend

export default function Upload({ onUpload, status, message, doc }) {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [localError, setLocalError] = useState("");

  const uploading = status === "uploading";
  const slow = useSlowFlag(uploading);

  function handleChange(event) {
    const chosen = event.target.files?.[0];
    setLocalError("");

    if (!chosen) {
      setFile(null);
      return;
    }

    if (!chosen.name.toLowerCase().endsWith(".pdf")) {
      setFile(null);
      setLocalError("Please choose a PDF file.");
      event.target.value = "";
      return;
    }

    if (chosen.size > MAX_FILE_MB * 1024 * 1024) {
      setFile(null);
      setLocalError(`File is too large. The maximum size is ${MAX_FILE_MB} MB.`);
      event.target.value = "";
      return;
    }

    setFile(chosen);
  }

  function handleUpload() {
    if (file && !uploading) onUpload(file);
  }

  // One status line: local problem first, then the upload result
  let banner = null;
  if (localError) {
    banner = { type: "error", text: localError };
  } else if (status === "uploading") {
    banner = {
      type: "loading",
      text: slow
        ? `${message} This is taking longer than usual - the server may be waking up.`
        : message,
    };
  } else if (status === "success") {
    banner = { type: "success", text: message };
  } else if (status === "error") {
    banner = { type: "error", text: message };
  }

  const bannerStyles = {
    loading: "border-accent/30 bg-accent/10 text-accent",
    success:
      "border-emerald-600/40 bg-emerald-500/10 text-emerald-800 dark:border-emerald-400/30 dark:text-emerald-300",
    error: "border-red-500/40 bg-red-500/10 text-red-800 dark:border-red-400/30 dark:text-red-300",
  };

  return (
    <section className="surface p-4 sm:p-5">
      <h2 className="text-base font-semibold text-fg">1. Upload your PDF</h2>
      <p className="mt-0.5 text-sm text-subtle">Text PDFs only, up to {MAX_FILE_MB} MB.</p>

      <div className="mt-4 space-y-3">
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          onChange={handleChange}
          disabled={uploading}
          className="hidden"
          id="pdf-input"
        />

        <div className="flex items-center gap-3">
          <label
            htmlFor="pdf-input"
            className={`btn-ghost shrink-0 cursor-pointer ${
              uploading ? "pointer-events-none opacity-50" : ""
            }`}
          >
            Choose PDF
          </label>

          <span className="min-w-0 flex-1 truncate text-sm text-muted">
            {file ? file.name : "No file chosen"}
          </span>
        </div>

        <button
          type="button"
          onClick={handleUpload}
          disabled={!file || uploading}
          className="btn-primary w-full"
        >
          {uploading && (
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-on-accent border-t-transparent" />
          )}
          {uploading ? "Processing..." : "Upload PDF"}
        </button>
      </div>

      {banner && (
        <div
          role="status"
          aria-live="polite"
          className={`mt-3 rounded-xl border px-3 py-2 text-sm ${bannerStyles[banner.type]}`}
        >
          {banner.text}
        </div>
      )}

      {doc && (
        <p className="mt-3 flex items-start gap-2 text-sm text-muted">
          <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-emerald-400" aria-hidden="true" />
          <span className="min-w-0 break-words">
            Ready: <span className="font-medium text-fg">{doc.filename}</span> - {doc.pages}{" "}
            pages, {doc.chunks} chunks
          </span>
        </p>
      )}
    </section>
  );
}

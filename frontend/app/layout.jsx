import "./globals.css";
import { DEFAULT_THEME, themeInitScript } from "@/lib/theme";

export const metadata = {
  title: "RAG Chatbot",
  description:
    "Upload a PDF and ask questions about it. Answers come only from your document and show the source pages.",
};

export const viewport = {
  themeColor: "#000000",
  colorScheme: "dark",
};

export default function RootLayout({ children }) {
  return (
    // suppressHydrationWarning: the small script below sets data-theme before React starts
    <html lang="en" data-theme={DEFAULT_THEME} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className="min-h-dvh bg-black text-zinc-100 antialiased">{children}</body>
    </html>
  );
}

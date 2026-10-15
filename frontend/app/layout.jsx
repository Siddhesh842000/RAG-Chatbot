import "./globals.css";
import { DEFAULT_MODE, DEFAULT_THEME, themeInitScript } from "@/lib/theme";

export const metadata = {
  title: "RAG Chatbot",
  description:
    "Upload a PDF and ask questions about it. Answers come only from your document and show the source pages.",
};

export default function RootLayout({ children }) {
  return (
    // suppressHydrationWarning: the small script below sets the theme before React starts
    <html lang="en" data-theme={DEFAULT_THEME} data-mode={DEFAULT_MODE} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className="min-h-dvh antialiased">{children}</body>
    </html>
  );
}

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FATE Console — Fully Automated Task Executive",
  description: "OS-level automation client for local macOS Apple Silicon scheduling and agentic intelligence.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body>{children}</body>
    </html>
  );
}

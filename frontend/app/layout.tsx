import "./globals.css";
import type { Metadata } from "next";
import { ReactNode } from "react";


// This metadata makes the app feel intentional when shared or deployed later.
export const metadata: Metadata = {
  title: "AI RAG Assistant",
  description: "A grounded study and research assistant with retrieval and citations."
};


// The root layout wraps the app router pages and loads the global visual system.
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}


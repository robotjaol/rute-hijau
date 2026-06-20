import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RuteHijau – Optimasi Rute Pengangkutan Sampah",
  description: "Susun rute pengangkutan sampah yang hemat untuk armada terbatas.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}

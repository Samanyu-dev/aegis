import type { Metadata } from "next";
import { Outfit, Share_Tech_Mono } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800", "900"],
});

const shareTechMono = Share_Tech_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400"],
});

export const metadata: Metadata = {
  title: "AEGIS — Autonomous Enterprise Intelligence Operating System",
  description: "Continuous live-web scans, persistent memory graphs, and automated trigger dispatches. Empowering compliance, security, and GTM teams at scale.",
  icons: {
    icon: "/favicon.ico",
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${outfit.variable} ${shareTechMono.variable} h-full antialiased font-sans`}
    >
      <body className="min-h-full flex flex-col bg-[#050508] text-slate-100 selection:bg-cyan-500/30 selection:text-cyan-200">
        {children}
      </body>
    </html>
  );
}

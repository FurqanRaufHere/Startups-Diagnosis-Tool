import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Venture Lens",
  description: "AI-powered startup due diligence diagnosis",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="bg-orb bg-orb-a" />
        <div className="bg-orb bg-orb-b" />
        {children}
      </body>
    </html>
  );
}

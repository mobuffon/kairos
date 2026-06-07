import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Kairos",
  description: "Personal leisure assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui, sans-serif", margin: 0, padding: "1.5rem" }}>
        <nav style={{ marginBottom: "1.5rem" }}>
          <a href="/" style={{ marginRight: "1rem" }}>Home</a>
          <a href="/dashboard" style={{ marginRight: "1rem" }}>Dashboard</a>
          <a href="/onboard" style={{ marginRight: "1rem" }}>Onboard</a>
          <a href="/settings">Settings</a>
        </nav>
        {children}
      </body>
    </html>
  );
}

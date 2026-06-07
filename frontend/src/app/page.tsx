import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      <h1>Kairos</h1>
      <p>Your personal leisure assistant — surf, ride, connect.</p>
      <p>
        <Link href="/dashboard">Open dashboard</Link> to preview mock suggestions for Mo.
      </p>
    </main>
  );
}

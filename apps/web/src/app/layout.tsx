import type { Metadata } from "next";
import Link from "next/link";
import { REPO_URL, SITE_URL, TRIBE_URL } from "@/lib/links";
import styles from "./layout.module.css";
import "./globals.css";

const description =
  "Free, open-source reports on how an average brain is predicted to respond to your reel, second by second, using Meta FAIR's TRIBE v2.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Reel Brain Report",
    template: "%s · Reel Brain Report",
  },
  description,
  openGraph: {
    type: "website",
    siteName: "Reel Brain Report",
    title: "Reel Brain Report",
    description,
    url: "/",
  },
  twitter: { card: "summary", title: "Reel Brain Report", description },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <header className={styles.header}>
          <div className={`container ${styles.headerInner}`}>
            <Link href="/" className={styles.brand}>
              Reel Brain Report
            </Link>
            <nav className={styles.nav} aria-label="Main">
              <Link href="/report/sample">Sample report</Link>
              <Link href="/about">About</Link>
              <a href={REPO_URL}>GitHub</a>
            </nav>
          </div>
        </header>
        <main className={styles.main}>{children}</main>
        <footer className={styles.footer}>
          <div className="container">
            <p>
              Predictions by <a href={TRIBE_URL}>TRIBE v2</a> from Meta FAIR, used under{" "}
              <a href="https://creativecommons.org/licenses/by-nc/4.0/">CC BY-NC 4.0</a>. Text
              features use Llama 3.2 (Llama 3.2 Community License). We summarise the model&apos;s
              output into regions and add rule-based insights; the model itself is unchanged.
            </p>
            <p>
              Free and open source (MIT). Not affiliated with or endorsed by Meta.{" "}
              <Link href="/about">About, privacy and licenses</Link>
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}

import Link from "next/link";
import { ReportOpener } from "@/components/ReportOpener";
import { COLAB_URL, LLAMA_URL } from "@/lib/links";
import styles from "./page.module.css";

export default function Home() {
  return (
    <div className="container">
      <section className={styles.hero}>
        <h1>See how a brain is predicted to respond to your reel</h1>
        <p className={styles.lead}>
          A second-by-second report on your reel: how strong the hook is, where attention is
          predicted to dip, whether visuals, faces, sound or speech carry it, and three things to
          fix. Free and open source. <Link href="/report/sample">See an example</Link>.
        </p>
      </section>

      <section className={styles.steps} aria-labelledby="steps-title">
        <h2 id="steps-title">Get your report</h2>
        <ol>
          <li>
            <h3>Run the notebook</h3>
            <p className="secondary">
              It runs on Google Colab&apos;s free GPU. You need a Hugging Face token with access to{" "}
              <a href={LLAMA_URL}>Llama 3.2</a> (one-time request). Reels up to 60 seconds; expect
              15–40 minutes.
            </p>
            <a className="button" href={COLAB_URL} target="_blank" rel="noreferrer">
              Open in Colab
            </a>
          </li>
          <li>
            <h3>Download report.zip</h3>
            <p className="secondary">The last step of the notebook saves it to your computer.</p>
          </li>
          <li>
            <h3>Open it here</h3>
            <ReportOpener />
          </li>
        </ol>
      </section>

      <p className="secondary">
        Your video stays in your own Colab session.{" "}
        <Link href="/about">How it works, privacy and licenses</Link>.
      </p>
    </div>
  );
}

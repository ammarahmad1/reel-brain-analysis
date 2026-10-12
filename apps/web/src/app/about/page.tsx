import type { Metadata } from "next";
import { REPO_URL, TRIBE_URL } from "@/lib/links";
import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "About",
  description:
    "How Reel Brain Report works, what it can and can't tell you, privacy, and licenses.",
};

export default function AboutPage() {
  return (
    <article className={`container ${styles.article}`}>
      <h1>About</h1>
      <p className={styles.lead}>
        Reel Brain Report is a free, open-source tool that shows how an average brain is predicted
        to respond to a short video, second by second.
      </p>

      <h2>How it works</h2>
      <p>
        You run your reel through <a href={TRIBE_URL}>TRIBE v2</a>, a brain-encoding model from Meta
        FAIR, in a Google Colab notebook. It predicts the fMRI response of an average person at
        about 20,000 points on the brain&apos;s surface, once per second, from the video, the audio
        and the spoken words.
      </p>
      <p>
        Those predictions are averaged over regions of the Destrieux atlas: visual cortex for{" "}
        <strong>visuals</strong>, the fusiform gyrus for <strong>faces</strong>, auditory cortex for{" "}
        <strong>sound</strong> and language areas for <strong>speech</strong>. A small set of fixed
        rules turns that into the hook rating, the dips, the channel that carries the reel and the
        top three fixes. The rules and thresholds are documented in the{" "}
        <a href={`${REPO_URL}/blob/main/docs/report-methodology.md`}>methodology</a>.
      </p>

      <h2>What it can and can&apos;t tell you</h2>
      <ul>
        <li>
          These are <strong>model predictions for an average brain</strong>, not measurements of you
          or your audience.
        </li>
        <li>
          Scores compare moments <strong>within the same reel</strong>. A weak hook is weak next to
          the rest of that reel, not next to other people&apos;s reels.
        </li>
        <li>
          A predicted brain response isn&apos;t attention, enjoyment or views. Nothing here promises
          engagement.
        </li>
        <li>The region groupings are coarse and the rules are deliberately simple.</li>
      </ul>

      <h2>Privacy</h2>
      <ul>
        <li>Your video is processed in your own Colab session. It never reaches this site.</li>
        <li>
          Reports open in your browser. The zip is read locally and isn&apos;t uploaded anywhere.
        </li>
        <li>No accounts, no ads, no tracking.</li>
      </ul>

      <h2>Open source</h2>
      <p>
        The code is on <a href={REPO_URL}>GitHub</a> under the MIT license. The models it downloads
        keep their own licenses (below), which only allow non-commercial use of TRIBE v2.
      </p>

      <h2>Credits and licenses</h2>
      <ul>
        <li>
          <strong>TRIBE v2</strong> by Meta FAIR (<a href={TRIBE_URL}>GitHub</a>), under{" "}
          <a href="https://creativecommons.org/licenses/by-nc/4.0/">CC BY-NC 4.0</a>.
        </li>
        <li>
          <strong>Llama 3.2</strong> by Meta, used by TRIBE v2 for text features, under the{" "}
          <a href="https://www.llama.com/llama3_2/license/">Llama 3.2 Community License</a>. Built
          with Llama.
        </li>
        <li>
          <strong>What we changed:</strong> nothing in the models. We average their predictions over
          atlas regions, score them within each reel, apply fixed rules and render brain images with
          nilearn.
        </li>
        <li>Brain atlas: Destrieux et al. (2010) on the FreeSurfer fsaverage5 surface.</li>
      </ul>
      <p className="muted">Not affiliated with or endorsed by Meta.</p>
    </article>
  );
}

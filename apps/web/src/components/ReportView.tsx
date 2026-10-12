import Image from "next/image";
import {
  CHANNEL_META,
  RATING_META,
  formatSpan,
  formatZ,
  type Report,
  type WindowScore,
} from "@/lib/report";
import { Timeline } from "./Timeline";
import styles from "./ReportView.module.css";

type Props = {
  report: Report;
  imageSrc: (file: string) => string;
};

export function ReportView({ report, imageSrc }: Props) {
  const { insights, fixes, heatmaps } = report;
  const carrier = insights.carrier.channel;

  return (
    <div className={styles.root}>
      <p className={styles.disclaimer} role="note">
        <strong>Model predictions, not measurements.</strong> {report.disclaimer}
      </p>

      <section aria-labelledby="summary-title">
        <h2 id="summary-title" className="visually-hidden">
          Summary
        </h2>
        <div className={styles.tiles}>
          <RatingTile title={`Hook (first ${insights.hook.end_s}s)`} score={insights.hook} />
          <RatingTile title="Ending" score={insights.ending} />
          <div className={`card ${styles.tile}`}>
            <span className={styles.tileTitle}>Peak moment</span>
            <span className={styles.tileValue}>{insights.peak.second}s</span>
            <span className={styles.tileNote}>{formatZ(insights.peak.z)} vs. reel average</span>
          </div>
          <div className={`card ${styles.tile}`}>
            <span className={styles.tileTitle}>Carried by</span>
            <span className={styles.tileValue}>
              {carrier ? CHANNEL_META[carrier].label : "No single channel"}
            </span>
            <span className={styles.tileNote}>
              {carrier
                ? "Tracks the overall ups and downs most closely"
                : "No channel tracks the overall response closely"}
            </span>
          </div>
        </div>
      </section>

      <section className="card" aria-labelledby="fixes-title">
        <h2 id="fixes-title">Top {fixes.length} fixes</h2>
        <ol className={styles.fixes}>
          {fixes.map((fix) => {
            const span = formatSpan(fix.start_s, fix.end_s);
            return (
              <li key={fix.id} className={styles.fix}>
                <div className={styles.fixHead}>
                  <h3>{fix.title}</h3>
                  {span && !fix.title.includes(span) && <span className={styles.chip}>{span}</span>}
                </div>
                <p className="secondary">{fix.detail}</p>
              </li>
            );
          })}
        </ol>
      </section>

      <Timeline report={report} />

      {insights.dips.length > 0 && (
        <section className="card" aria-labelledby="dips-title">
          <h2 id="dips-title">Dips</h2>
          <ul className={styles.dips}>
            {insights.dips.map((d) => (
              <li key={d.start_s}>
                <strong>{formatSpan(d.start_s, d.end_s)}</strong>: lowest at {d.lowest_second}s (
                {formatZ(d.min_z)}), mostly in {CHANNEL_META[d.weakest_channel].noun}.
              </li>
            ))}
          </ul>
          {!insights.speech.detected && (
            <p className="muted">
              Only {insights.speech.word_count} spoken word
              {insights.speech.word_count === 1 ? " was" : "s were"} detected, so dips aren&apos;t
              attributed to speech.
            </p>
          )}
        </section>
      )}

      {heatmaps.length > 0 && (
        <section className="card" aria-labelledby="heatmaps-title">
          <h2 id="heatmaps-title">Brain heatmaps</h2>
          <p className="secondary">
            Predicted response on the brain&apos;s surface (left and right hemispheres, side view).
            Warm colours are above zero, cool colours below. Faint values are hidden so the anatomy
            shows through. All images share one colour scale.
          </p>
          <div className={styles.heatmaps}>
            {heatmaps.map((h) => (
              <figure key={h.kind} className={styles.heatmap}>
                <Image
                  src={imageSrc(h.file)}
                  alt={`Brain heatmap: ${h.label}`}
                  width={677}
                  height={413}
                  unoptimized
                />
                <figcaption>{h.label}</figcaption>
              </figure>
            ))}
          </div>
        </section>
      )}

      <p className="muted">
        Scores compare moments within this reel, so a &quot;weak&quot; hook is weak relative to the
        rest of the same reel, not to other reels. Video length:{" "}
        {report.video.duration_s.toFixed(1)}s.
      </p>
    </div>
  );
}

function RatingTile({ title, score }: { title: string; score: WindowScore }) {
  const meta = RATING_META[score.rating];
  return (
    <div className={`card ${styles.tile}`}>
      <span className={styles.tileTitle}>{title}</span>
      <span className={`${styles.tileValue} ${styles[meta.tone]}`}>
        <span aria-hidden>{meta.icon}</span> {meta.label}
      </span>
      <span className={styles.tileNote}>{formatZ(score.score_z)} vs. reel average</span>
    </div>
  );
}

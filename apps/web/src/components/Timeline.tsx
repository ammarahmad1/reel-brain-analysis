"use client";

import { useEffect, useRef, useState } from "react";
import { CHANNEL_META, CHANNELS, formatZ, type Insights, type Report } from "@/lib/report";
import styles from "./Timeline.module.css";

const PAD = { top: 10, right: 12, bottom: 22, left: 34 };

type Scale = {
  width: number;
  extent: number;
  seconds: number[];
  x: (s: number) => number;
};

export function Timeline({ report }: { report: Report }) {
  const { timeline, insights } = report;
  const { seconds } = timeline;
  const ref = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);
  const [hover, setHover] = useState<number | null>(null);
  const [showTable, setShowTable] = useState(false);

  useEffect(() => {
    if (!ref.current) return;
    const ro = new ResizeObserver(([e]) => setWidth(Math.floor(e.contentRect.width)));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);

  // Shared y-range so channels can be compared by eye.
  const all = [timeline.overall, ...CHANNELS.map((c) => timeline.channels[c])].flat();
  const extent = Math.max(2, Math.ceil(Math.max(...all.map(Math.abs)) * 2) / 2);
  const xMax = seconds[seconds.length - 1] + 1;
  const plotW = Math.max(0, width - PAD.left - PAD.right);
  const scale: Scale = { width, extent, seconds, x: (s) => PAD.left + (s / xMax) * plotW };

  function onPointerMove(e: React.PointerEvent<HTMLDivElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const s = ((e.clientX - rect.left - PAD.left) / plotW) * xMax - 0.5;
    const nearest = seconds.reduce(
      (best, sec, i) => (Math.abs(sec - s) < Math.abs(seconds[best] - s) ? i : best),
      0,
    );
    setHover(nearest);
  }

  function onKeyDown(e: React.KeyboardEvent) {
    const last = seconds.length - 1;
    if (e.key === "ArrowRight") setHover((h) => Math.min(last, (h ?? -1) + 1));
    else if (e.key === "ArrowLeft") setHover((h) => Math.max(0, (h ?? last + 1) - 1));
    else if (e.key === "Escape") setHover(null);
    else return;
    e.preventDefault();
  }

  return (
    <section className={`card ${styles.root}`} aria-labelledby="timeline-title">
      <div className={styles.header}>
        <div>
          <h2 id="timeline-title">Second by second</h2>
          <p className="secondary">
            Predicted response compared with this reel&apos;s own average. Hover or use the arrow
            keys to read any second.
          </p>
        </div>
        <button type="button" className="button ghost" onClick={() => setShowTable((v) => !v)}>
          {showTable ? "Hide table" : "Show table"}
        </button>
      </div>

      <ul className={styles.legend}>
        <li>
          <span className={styles.swatch} style={{ background: "var(--band-hook)" }} />
          Hook ({insights.hook.start_s}–{insights.hook.end_s}s)
        </li>
        {insights.dips.length > 0 && (
          <li>
            <span className={styles.swatch} style={{ background: "var(--band-dip)" }} />
            Dip
          </li>
        )}
      </ul>

      <div
        ref={ref}
        className={styles.plots}
        tabIndex={0}
        role="group"
        aria-label="Timeline chart. Use the left and right arrow keys to move between seconds."
        onPointerMove={onPointerMove}
        onPointerLeave={() => setHover(null)}
        onKeyDown={onKeyDown}
        onBlur={() => setHover(null)}
      >
        <Panel
          label="Overall"
          values={timeline.overall}
          color="var(--series-overall)"
          height={200}
          scale={scale}
          hover={hover}
          insights={insights}
        />
        <div className={styles.channels}>
          {CHANNELS.map((c) => (
            <Panel
              key={c}
              label={CHANNEL_META[c].label}
              values={timeline.channels[c]}
              color={CHANNEL_META[c].color}
              height={120}
              scale={scale}
              hover={hover}
            />
          ))}
        </div>
      </div>

      <p className="visually-hidden" aria-live="polite">
        {hover !== null &&
          `${seconds[hover]} seconds: overall ${formatZ(timeline.overall[hover])}, ` +
            CHANNELS.map(
              (c) => `${CHANNEL_META[c].label} ${formatZ(timeline.channels[c][hover])}`,
            ).join(", ")}
      </p>

      {showTable && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <caption className="visually-hidden">Scores per second, relative to this reel</caption>
            <thead>
              <tr>
                <th scope="col">Second</th>
                <th scope="col">Overall</th>
                {CHANNELS.map((c) => (
                  <th scope="col" key={c}>
                    {CHANNEL_META[c].label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {seconds.map((s, i) => (
                <tr key={s}>
                  <th scope="row">{s}s</th>
                  <td>{formatZ(timeline.overall[i])}</td>
                  {CHANNELS.map((c) => (
                    <td key={c}>{formatZ(timeline.channels[c][i])}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

type PanelProps = {
  label: string;
  values: number[];
  color: string;
  height: number;
  scale: Scale;
  hover: number | null;
  insights?: Insights; // only the overall panel shows hook/dip bands and the peak
};

function Panel({ label, values, color, height, scale, hover, insights }: PanelProps) {
  const { width, extent, seconds, x } = scale;
  const plotH = height - PAD.top - PAD.bottom;
  const y = (v: number) => PAD.top + ((extent - v) / (2 * extent)) * plotH;
  const mid = (s: number) => x(s + 0.5); // a value covers its whole second
  const path = values.map((v, i) => `${i ? "L" : "M"}${mid(seconds[i])},${y(v)}`).join("");
  const yTicks = insights ? [-extent, 0, extent] : [0];
  const peakIndex = insights ? seconds.indexOf(insights.peak.second) : -1;

  const band = (start: number, end: number, fill: string) => (
    <rect
      key={`${fill}${start}`}
      x={x(start)}
      y={PAD.top}
      width={x(end) - x(start)}
      height={plotH}
      fill={fill}
    />
  );

  return (
    <div className={styles.panel}>
      <div className={styles.panelHead}>
        <span className={styles.key} style={{ background: color }} aria-hidden />
        <span className={styles.panelLabel}>{label}</span>
        <span className={styles.panelValue}>
          {hover !== null && `${formatZ(values[hover])} at ${seconds[hover]}s`}
        </span>
      </div>
      {width > 0 && (
        <svg width={width} height={height} aria-hidden className={styles.svg}>
          {insights && band(insights.hook.start_s, insights.hook.end_s, "var(--band-hook)")}
          {insights?.dips.map((d) => band(d.start_s, d.end_s, "var(--band-dip)"))}
          {yTicks.map((t) => (
            <g key={t}>
              <line
                x1={PAD.left}
                x2={width - PAD.right}
                y1={y(t)}
                y2={y(t)}
                stroke={t === 0 ? "var(--axis)" : "var(--grid)"}
              />
              <text x={PAD.left - 6} y={y(t)} dy="0.32em" textAnchor="end" className={styles.tick}>
                {t === 0 ? "avg" : formatZ(t)}
              </text>
            </g>
          ))}
          {seconds
            .filter((s) => s % 5 === 0)
            .map((s) => (
              <text key={s} x={x(s)} y={height - 6} textAnchor="middle" className={styles.tick}>
                {s}s
              </text>
            ))}
          <path d={path} fill="none" stroke={color} strokeWidth={2} strokeLinejoin="round" />
          {peakIndex >= 0 && (
            <>
              <circle
                cx={mid(seconds[peakIndex])}
                cy={y(values[peakIndex])}
                r={4.5}
                fill={color}
                stroke="var(--surface)"
                strokeWidth={2}
              />
              <text
                x={mid(seconds[peakIndex])}
                y={y(values[peakIndex]) - 10}
                textAnchor="middle"
                className={styles.annotation}
              >
                Peak
              </text>
            </>
          )}
          {hover !== null && (
            <>
              <line
                x1={mid(seconds[hover])}
                x2={mid(seconds[hover])}
                y1={PAD.top}
                y2={PAD.top + plotH}
                stroke="var(--text-muted)"
              />
              <circle
                cx={mid(seconds[hover])}
                cy={y(values[hover])}
                r={4}
                fill={color}
                stroke="var(--surface)"
                strokeWidth={2}
              />
            </>
          )}
        </svg>
      )}
    </div>
  );
}

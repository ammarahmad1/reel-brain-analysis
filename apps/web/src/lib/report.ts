import type { Channel, Report, WindowScore } from "./report.generated";

export type * from "./report.generated";

export const CHANNELS: Channel[] = ["visual", "faces", "sound", "speech"];

export const CHANNEL_META: Record<Channel, { label: string; noun: string; color: string }> = {
  visual: { label: "Visual", noun: "visuals", color: "var(--series-visual)" },
  faces: { label: "Faces", noun: "faces", color: "var(--series-faces)" },
  sound: { label: "Sound", noun: "sound", color: "var(--series-sound)" },
  speech: { label: "Speech", noun: "speech", color: "var(--series-speech)" },
};

export const RATING_META: Record<
  WindowScore["rating"],
  { label: string; icon: string; tone: "good" | "neutral" | "serious" }
> = {
  strong: { label: "Strong", icon: "▲", tone: "good" },
  average: { label: "Average", icon: "●", tone: "neutral" },
  weak: { label: "Weak", icon: "▼", tone: "serious" },
};

export const SCHEMA_VERSION = "0.1.0";

/** "+1.2", "−0.7", "±0.0" */
export function formatZ(z: number): string {
  const v = Math.abs(z) < 0.05 ? 0 : z;
  return `${v > 0 ? "+" : v < 0 ? "−" : "±"}${Math.abs(v).toFixed(1)}`;
}

export function formatSpan(start: number | null, end: number | null): string | null {
  if (start === null || end === null) return null;
  return end - start <= 1 ? `${start}s` : `${start}–${end}s`;
}

/** Shallow check of a report.json from the notebook. Throws a readable error. */
export function parseReport(text: string): Report {
  let data: unknown;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error("report.json isn't valid JSON.");
  }
  const r = data as Partial<Report>;
  if (r?.schema_version !== SCHEMA_VERSION) {
    throw new Error(
      `This report was made with a different version (${String(r?.schema_version)}). ` +
        "Re-run the latest notebook.",
    );
  }
  const n = r.timeline?.seconds?.length ?? 0;
  const lengthsMatch =
    n > 0 &&
    r.timeline!.overall?.length === n &&
    CHANNELS.every((c) => r.timeline!.channels?.[c]?.length === n);
  if (!lengthsMatch || !r.insights || !Array.isArray(r.fixes) || !Array.isArray(r.heatmaps)) {
    throw new Error("report.json is missing parts of the report.");
  }
  return r as Report;
}

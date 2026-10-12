"use client";

import { unzipSync } from "fflate";
import { useEffect, useRef, useState } from "react";
import { parseReport, type Report } from "@/lib/report";
import { ReportView } from "./ReportView";
import styles from "./ReportOpener.module.css";

const MAX_ZIP_MB = 25;

type Loaded = { report: Report; images: Map<string, string>; name: string };

async function readReportZip(file: File): Promise<Loaded> {
  if (file.size > MAX_ZIP_MB * 1e6) throw new Error(`That file is over ${MAX_ZIP_MB} MB.`);

  let entries: Record<string, Uint8Array>;
  try {
    entries = unzipSync(new Uint8Array(await file.arrayBuffer()));
  } catch {
    throw new Error("That doesn't look like a zip file. Use the report.zip from the notebook.");
  }

  // Match by file name so it works whether or not the zip has a top-level folder.
  const byName = new Map(
    Object.entries(entries).map(([path, data]) => [path.split("/").pop()!, data]),
  );
  const json = byName.get("report.json");
  if (!json) throw new Error("No report.json inside that zip.");
  const report = parseReport(new TextDecoder().decode(json));

  const images = new Map<string, string>();
  for (const { file: name } of report.heatmaps) {
    const data = byName.get(name);
    if (data)
      images.set(name, URL.createObjectURL(new Blob([data as BlobPart], { type: "image/png" })));
  }
  report.heatmaps = report.heatmaps.filter((h) => images.has(h.file));
  return { report, images, name: file.name };
}

export function ReportOpener() {
  const input = useRef<HTMLInputElement>(null);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  useEffect(() => () => loaded?.images.forEach((url) => URL.revokeObjectURL(url)), [loaded]);

  async function open(file: File | undefined) {
    if (!file) return;
    setError(null);
    try {
      setLoaded(await readReportZip(file));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't open that file.");
    }
  }

  if (loaded) {
    return (
      <div className={styles.loaded}>
        <div className={styles.bar}>
          <span className="secondary">
            Showing <strong>{loaded.name}</strong>
          </span>
          <button type="button" className="button ghost" onClick={() => setLoaded(null)}>
            Open another report
          </button>
        </div>
        <ReportView report={loaded.report} imageSrc={(f) => loaded.images.get(f) ?? ""} />
      </div>
    );
  }

  return (
    <div>
      <div
        className={`${styles.drop} ${dragging ? styles.dragging : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          open(e.dataTransfer.files[0]);
        }}
      >
        <p className={styles.title}>Drop your report.zip here</p>
        <p className="muted">It opens right here in your browser. Nothing is uploaded.</p>
        <button type="button" className="button" onClick={() => input.current?.click()}>
          Choose report.zip
        </button>
        <input
          ref={input}
          type="file"
          accept=".zip,application/zip"
          className="visually-hidden"
          onChange={(e) => open(e.target.files?.[0])}
        />
      </div>
      <p aria-live="polite" className={styles.error}>
        {error}
      </p>
    </div>
  );
}

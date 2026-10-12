import type { Metadata } from "next";
import { ReportView } from "@/components/ReportView";
import type { Report } from "@/lib/report";
import sample from "@/data/sample-report.json";

export const metadata: Metadata = {
  title: "Sample report",
  description: "An example brain-response report for a 23-second music reel.",
};

// Regenerate with: .venv/Scripts/python scripts/build_sample_report.py
const report = sample as Report;

export default function SampleReportPage() {
  return (
    <div className="container">
      <h1>Sample report</h1>
      <p className="secondary">A real report for a 23-second music reel with almost no speech.</p>
      <ReportView report={report} imageSrc={(f) => `/sample/${f}`} />
    </div>
  );
}

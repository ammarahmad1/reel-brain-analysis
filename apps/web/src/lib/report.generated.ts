/* Generated from packages/report-schema/report.schema.json by npm run gen:types. Do not edit. */

/**
 * @minItems 1
 */
export type Series = number[];
export type Channel = "visual" | "faces" | "sound" | "speech";

/**
 * Contract between the worker (packages/report) and the frontend. Scores are within-reel z-scores.
 */
export interface Report {
  schema_version: "0.1.0";
  video: {
    duration_s: number;
  };
  timeline: Timeline;
  insights: Insights;
  heatmaps: Heatmap[];
  credits: {
    model: string;
    model_url: string;
    model_license: string;
    text_model?: string;
  };
}
export interface Timeline {
  /**
   * @minItems 1
   */
  seconds: number[];
  overall: Series;
  channels: {
    visual: Series;
    faces: Series;
    sound: Series;
    speech: Series;
  };
}
export interface Insights {
  hook: WindowScore;
  ending: WindowScore;
  peak: Moment;
  low: Moment;
  dips: Dip[];
  carrier: Carrier;
  speech: {
    word_count: number;
    detected: boolean;
  };
}
export interface WindowScore {
  start_s: number;
  end_s: number;
  score_z: number;
  rating: "strong" | "average" | "weak";
}
export interface Moment {
  second: number;
  z: number;
}
export interface Dip {
  start_s: number;
  end_s: number;
  min_z: number;
  lowest_second: number;
  weakest_channel: Channel;
}
export interface Carrier {
  channel: Channel | null;
  correlations: {
    [k: string]: number;
  };
}
export interface Heatmap {
  kind: "average" | "hook" | "peak" | "dip";
  label: string;
  second: number | null;
  file: string;
}

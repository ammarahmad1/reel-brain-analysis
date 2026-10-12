# Report viewer

Next.js app that renders a `report.json` from the notebook. Reports are opened entirely in the browser:
the zip is read with [fflate](https://github.com/101arrowz/fflate) and nothing is uploaded.

```sh
npm install
npm run dev          # http://localhost:3000
npm run build
npm run lint && npm run typecheck
npm run gen:types    # regenerate src/lib/report.generated.ts from the JSON Schema
```

The sample report at `/report/sample` comes from `src/data/sample-report.json` and `public/sample/*.png`,
both produced by `scripts/build_sample_report.py` in the repo root.

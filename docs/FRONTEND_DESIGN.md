# Frontend Design

**Status:** Brand, product positioning, restrained futuristic/technical style, dark and light themes, lime accent, and developer-focused personality are **CONFIRMED**. Palette values and interface patterns below are initial tokens/proposals to validate for accessibility and usability, not final production measurements.

## Brand positioning

**EvalForge — The AI Systems Control Room.**
**Understand every trace. Investigate every failure.**

The UI helps engineers inspect execution, not converse with a generic assistant. Its signature is trace geometry (branching paths and nested spans), selective Signal Lime activity, technical typography, and a readable waterfall.

## Visual personality and rules

Precise, intelligent, technical, confident; futuristic without science-fiction decoration. Data-dense but calm, with clear hierarchy, consistent spacing, restrained effects, and purposeful use of color. No generic AI-dashboard composition.

## Initial color tokens

| Token | Dark | Light | Status |
|---|---|---|---|
| Canvas | `#0D1218` | `#F5F7F3` | Proposed |
| Surface | `#151D26` | `#FFFFFF` | Proposed |
| Elevated surface | `#202B35` | `#E8EDE5` | Proposed |
| Primary text | `#EAF0E8` | `#19231B` | Proposed |
| Signal Lime | `#B8F04A` | `#B8F04A` | Confirmed accent value; contrast/use must be validated |

Semantic success, error, warning, and information colors must be distinct and consistent in both themes. Lime is not a substitute for semantic status. Selected, focus, and disabled states need separate tokens. Exact semantic hex values and contrast pairings remain **UNRESOLVED** pending contrast tests; do not guess that the supplied lime works for small text.

## Typography

Geist or Inter is proposed for interface text; JetBrains Mono for trace IDs, timestamps, model names, token counts, and code-like values. Font selection, loading strategy, scale, and fallback stack remain open. Use tabular numerals where numeric alignment improves scanning.

## Layout, spacing, components

Use a consistent spacing scale and compact but legible data rows; final values are proposals to validate with real trace density. Favor semantic page layouts over universal cards. Navigation should make project context explicit. Tables should support understandable sorting/filtering, stable columns, empty/loading/error states, and keyboard access. Panels should expose hierarchy without nested-card clutter. Avoid excessive rounding, gradients, glow, glass effects, oversized decorative cards, and animation.

Component behavior should be predictable across themes: buttons, inputs, filters, tables, badges, tooltips, dialogs, code/ID copy actions, and empty states need focus, hover, disabled, and error states. Selected lime highlights should not be the sole indicator.

## Themes and accessibility

Both dark and light themes are intentional design requirements, not an inverted afterthought. Test text, chart series, borders, focus rings, and semantic colors for contrast in both. Preserve visible focus, meaningful labels, keyboard navigation, screen-reader names, reduced motion, non-color status cues, and usable zoom/reflow. WCAG target/version is **PROPOSED** and must be agreed; measure contrast rather than asserting untested compliance.

## Information architecture and page goals

| Page | Primary job | Design priority |
|---|---|---|
| Overview | Assess project health | Compact volume/error/latency/token/cost summaries and time-window context |
| Trace Explorer | Find a request | Filters, sortable list, useful status/duration/time/service metadata |
| Trace Detail | Reconstruct execution | Nested spans, errors, relationships, timing waterfall, event context |
| Event Explorer | Find occurrences | Searchable/filterable event list with trace/span links |
| Analytics | Understand trends | Readable metrics, sample counts, time buckets, comparisons |
| Anomaly/Insights | Triage changes | Explainable rule, observed interval, baseline/window, evidence link |
| AI Investigations | Review analysis | Findings first, facts vs hypotheses, evidence references, caveats |
| Projects | Select/manage workspaces | Clear ownership/project context and concise metadata |
| API Key Management | Create/revoke credentials | One-time secret display, masked metadata, revocation confirmation |
| Settings | Configure preferences | Explicit theme/privacy/project controls and safe defaults |

These are navigation areas, not finalized wireframes or a mandate for identical card layouts.

## Trace waterfall principles

- Use a shared time axis with explicit units, useful zoom/range behavior, and visible trace boundaries.
- Render nested parent-child paths and roots clearly; never imply that sequential ordering means causality.
- Show duration and offsets; parallel operations may overlap.
- Distinguish errors/retries with semantic shapes/color plus text/icon, not color alone.
- Handle very short spans, large span counts, missing timing, and long labels without losing navigability.
- Provide keyboard/screen-reader alternative descriptions or an accessible table/tree representation.
- Link selection between span details and related events; make selected state obvious.

Trace geometry is a signature concept, but performance and accessibility outrank decoration.

## Charts and tables

Every chart needs a title, unit, period, and sample context. Show missing/unknown cost distinctly from zero. Keep semantic colors stable. Avoid misleading axes and unexplained smoothing. Provide accessible summaries or tabular alternatives. Tables should support pagination/virtualization if volume warrants it; preserve sorting/filter context and give clear no-results vs no-data states.

## Responsive behavior

Desktop prioritizes dense trace inspection; narrower screens should preserve the critical sequence and details through deliberate collapse/reflow, not merely shrink desktop columns. Exact breakpoints and mobile feature parity are unresolved. Test keyboard operation, touch targets, horizontal overflow, and trace waterfall navigation at relevant widths.

## Interaction and motion

Use motion only to communicate state or relationships. Respect reduced-motion preference. Avoid looping animation, flashy transitions, and distracting effects. Confirm destructive key revocation; make investigation external data transfer explicit before submission.

## Anti-patterns

- Excessive neon, glow, or glassmorphism.
- Random gradients, AI sparkles, robots, brain graphics.
- Generic AI-generated SaaS dashboard template.
- Oversized decorative cards or unnecessary animation.
- Using lime for success/error/warning indiscriminately.
- Dense charts without units, time windows, or accessible alternatives.

## Research and unresolved decisions

No Figma community file or external design reference was inspected for this documentation task; Figma access/reference inspection was unavailable. No links or product-specific research findings are claimed. The palette and principles come from the supplied approved direction, not copied designs. Before implementation, inspect suitable developer/observability references if access is available and record sources and inspiration separately from decisions.

Unresolved: exact semantic palette, font choice/licensing/loading, spacing/type scales, responsive breakpoints, contrast target, project switcher/navigation, investigation consent UX, page wireframes, and chart behavior for sparse samples.

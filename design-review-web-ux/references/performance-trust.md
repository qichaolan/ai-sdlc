# Performance and trust baseline

## Responsiveness and measurement

- Keep three things distinct: how responsive the UI feels, measured rendering and interactivity, and the time the backend or an agent takes. Make delays understandable with immediate feedback, honest progress, cancellation where feasible, and context that stays in place.
- For field performance, use the "good" Core Web Vitals thresholds as provisional goals:
  - LCP of 2.5 s or less
  - INP of 200 ms or less
  - CLS of 0.1 or less

  Assess each at the 75th percentile, separately for mobile and desktop. Check the current definitions on web.dev before you cite them.
- Label every measurement as lab or field, and give its tooling, environment, sample, and date. Don't use Total Blocking Time in place of measured INP, and don't present one lab run as a field pass.
- Raise layout shift, expensive interactions, missing image dimensions, and long-list performance only when the evidence supports it. Don't invent timings, and don't prescribe virtualization without evidence about scale.

## Trust and user choice

- Review how clearly consent is asked for, any exposure of sensitive data, the explanations given for permission requests, and undo or confirmation for consequential actions.
- Flag deceptive patterns:
  - pre-checked opt-ins
  - hidden costs
  - false urgency or scarcity
  - confirmshaming
  - an obstructed cancellation flow
  - visual weight that nudges users toward the option that benefits the business

## AI features

- Distinguish generated content from verified content, and make sources and uncertainty easy to understand.
- Show the status of tools and actions, such as running, waiting for approval, done, or failed. Let users review consequential actions before they run.
- Keep streamed output readable and stable. Announce milestones to assistive technology rather than every token.

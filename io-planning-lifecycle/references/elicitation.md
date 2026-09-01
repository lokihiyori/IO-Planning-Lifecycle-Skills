# IO Flow Elicitation Rules

Use this reference in **Elicit** mode or whenever a missing answer would materially change classification, routing, service responsibility, persistence, lifecycle status, or version impact.

## Outcome and stopping rule

Elicitation produces confirmed answers for blocking decisions, or an explicitly incomplete draft when the user chooses to defer them. It is not an interview for its own sake.

Stop asking when every blocking gap is either answered or intentionally recorded as a blocking `OD-NN` item with an owner. Do not keep asking about wording, formatting, or low-impact metadata that can safely remain `unspecified` or TBD in a draft.

## Gap-to-question routing

| Gap | Question form | Why it blocks |
|---|---|---|
| Entry function, trigger, or expected output is ambiguous | Focused open question | The entry boundary cannot be modeled safely |
| Two or three evidenced classification schemes are plausible | Short selection question | The choice changes Type membership and routing |
| Classification precedence or boundary overlap is unclear | Selection question with concrete boundary examples | The same request may route to different loops |
| A Database, queue, archive, notification, verification, or AI step is uncertain | Ask whether it is required, optional/asynchronous, or absent | Service and consistency semantics change |
| Service order or ownership is contradictory | Show the conflicting alternatives and ask for the authoritative one | Silent reconciliation would invent a decision |
| Status advancement lacks evidence | Ask for the approval or implementation evidence | Status cannot be inferred from prose quality |
| Version impact is ambiguous after an accepted change | Show the affected IDs and the two plausible impact classes | Version history is a shared contract |

Do not offer invented options. A selection question must be grounded in the source, repository convention, or a clearly labeled design alternative. Use an open question when no bounded choices are defensible.

## Interaction protocol

1. Summarize the current model in one compact statement so the user can catch a wrong premise.
2. Ask one blocking question at a time when the next question depends on the answer. Group independent, low-complexity selections only when doing so reduces friction.
3. After each answer, state the exact affected `EP-NN`, Type, loop edge, decision, or status.
4. If the answer creates a new conflict, surface it before moving on.
5. Close with an answer ledger: confirmed decisions, deferred decisions, assumptions, and the resulting document status.
6. Generate or update the document only after the blocking ledger is closed, unless the user explicitly asks for an incomplete draft.

If the host supports structured selection controls, use them for two or three mutually exclusive choices. Otherwise present a concise numbered selection in conversation. Free-form follow-up is appropriate when the user must supply a service name, threshold, owner, or authoritative source.

## Elicit-mode invocation

```text
Use $io-planning-lifecycle in Elicit mode. Inspect this source, identify only the gaps that can change routing or service boundaries, ask me one blocking question at a time, and produce the IO Flow after the decision ledger is closed.
```

Elicit mode may end with a decision ledger and no file mutation when the user asks only for discovery or requirements clarification.

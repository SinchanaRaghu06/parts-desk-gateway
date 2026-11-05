# KSIT domain portal — event protocol

This is domainportal.v1. Existing calibration cohorts are reused for this human
rehearsal; they are not fresh competition finals. Follow BRIEF.md for task outcomes.

IST timetable on the organizer's explicitly configured event date: initial packet
08:00; coding 08:30–10:00, 12:00–14:00, 15:30–17:30; twist release 13:15;
final nomination cutoff and organizer-only private testing 17:45. Deployment alone
does not arm an event. Four official and four practice uploads per stage.
One public evaluation may be outstanding per team. Before 17:45 IST, captains
may withdraw their own queued or infrastructure-failed public work, including
an automatic retained evaluation. Withdrawal does not refund an accepted
attempt. Withdrawn work leaves selection without a score.

Submit a source ZIP with top-level solution.py exposing decide(observation,state),
returning exactly action and state objects. All preparation is inside the runnable
submission. Allowed files: .py, .json, .md, .txt; at most 100 files, each 2 MiB,
16 MiB uncompressed source total, 32 MiB upload. Links and nested paths forbidden.
Source is frozen by hash. Python 3.12 with numpy/pandas/scipy/sklearn is available.
Runs use pinned Docker, network disabled, UID 65534, 2 CPUs, 2 GiB, read-only source
and /public. 120-second response, 1200-second run, 1 MiB JSON frame limits apply.

Technical score: 20% pre validation + 30% post validation + 50% private final.
Post/final ordinary and changed conditions receive equal weight. Task grades are
0–100; no paperwork/approach-count/preprocessing points or lateness deductions.
Public board shows validation and provisional points out of 50. Private results
and traces are organizer-only. Initial source is retained and automatically run
post-twist. Later eligible source can replace it under validation-only selection.

Agentic teams host and pay for their own HTTPS model gateway, model and provider
keys. Other domains need no external paid service. The frozen controller emits
{op:llm,messages:[{role,content}],max_output_tokens:16..2048}; the trusted relay
returns observation.llm_response and llm_usage. 1–8 successful gateway requests
per case; calls do not consume world tool units. Messages: 1–24, at most 48,000
serialized bytes; request 64 KiB, response 128 KiB, model text 64 KiB. Each gateway
call has a 45-second overall deadline. No organizer inference or fallback.
Gateway POST HTTPS port 443 accepts {messages,max_output_tokens} and returns
{text,usage?}. Provide only a restricted gateway bearer token to the portal;
provider credentials remain on your infrastructure. Public IPs only; redirects,
URL credentials/query/fragment and non-443 ports are rejected. Use the portal's
generic gateway connection check. Endpoint revisions bind to receipts: changing
a gateway requires a new submission. Keep all submitted gateway revisions and
tokens available through 19:45 IST on the event date and until the organizer
announces final testing completion if testing is extended. Calls prove requests to your gateway, not
provider attestation; finalists must show real LLM usage and unchanged gateway/model
configuration with source and provider evidence. See GATEWAY.md and gateway_example.py.

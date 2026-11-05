# Team-owned inference gateway

Submit solution.py only with its source dependencies. Run gateway_example.py on
your infrastructure behind your HTTPS reverse proxy; do not submit the gateway
server or keys. Set TEAM_PROVIDER_URL (full OpenAI-compatible chat-completions URL),
TEAM_PROVIDER_KEY, TEAM_MODEL and TEAM_GATEWAY_TOKEN. Listen on 127.0.0.1:8080
and publish https://your-public-host/gateway on port 443. Configure ingress body,
time, concurrency and rate limits, and disable access/body logs. Keep provider
keys on your server. Register your public URL and restricted gateway token in the
portal, then use its generic connection check. No model or paid provider default
is supplied. Adapt this example for your own provider API if necessary.

The gateway accepts model messages and returns model text; it must not implement
a mutable world policy. Your submitted controller parses that text and chooses
world actions. Gateway/model changes need a new source receipt with a new endpoint
revision. Preserve submitted revisions/tokens through 19:45 IST and until announced final
testing completion if the organizer extends testing. Prompts may include
held-out observations and tool responses. Use the gateway for inference only.
Do not retain held-out prompts for later lookup or adapt server policy between
the frozen receipt and final testing. Finalist review checks actual model
inference and unchanged gateway/model configuration through source/provider evidence.

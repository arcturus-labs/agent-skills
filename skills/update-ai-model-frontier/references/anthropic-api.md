# Anthropic models through the direct API

Read this alongside the selected harness reference when the user requests Claude/Anthropic models via the API. Anthropic already belongs to the report watchlist and default chart. Use its own company frontier, retaining eligible thinking configurations, rather than only the combined frontier. Do not hardcode today's Claude model list.

## Credentials and routing

Use the harness's native Anthropic provider with an exported `ANTHROPIC_API_KEY`. If missing, direct the user to Settings → API keys in the [Claude Console](https://platform.claude.com/) and the [official authentication guide](https://platform.claude.com/docs/en/manage-claude/authentication). Check presence without printing the value. API billing/access must be enabled for the account; a Claude subscription or OAuth login does not by itself establish direct API-key access.

Inspect the installed harness's credential precedence before testing. Saved OAuth credentials or environment tokens may take precedence over an API key. Confirm the request uses the requested API-key route without logging credentials. Use a supported scoped credential override or isolated profile if needed; preserve existing logins. Do not pass a literal key in command arguments or delete an authentication store. Do not silently substitute OpenRouter, Bedrock, Vertex, or subscription authentication.

## Select and verify

1. Refresh the harness catalogue using its reference and inspect the built-in `anthropic` provider. Map each AA frontier record to an exact available API model ID. Prefer native definitions; add a custom definition only when necessary and verified against current provider and harness docs. Anthropic's native API is not an OpenAI-completions endpoint.
2. Verify model-specific thinking support. AA effort labels, adaptive thinking, and token budgets do not necessarily map one-to-one to harness effort names. Keep supported mappings, explain unavailable configurations, and never silently clamp an unsupported level while claiming benchmark equivalence.
3. Add verified `anthropic/MODEL_ID:EFFORT` selections to the requested harness's scoped list using its documented syntax. Preserve unrelated selections and defaults unless replacement was requested. If no supported effort suffix applies, use the harness's supported selector form.
4. Verify catalogue registration and scoped inclusion, then make minimal live requests at the selected effort through the API-key route using the harness's isolation options. Report which configurations were actually tested. Distinguish authentication errors, unavailable model IDs, unsupported thinking settings, balance/quota errors, and local permissions.
5. Report unavailable frontier records and the reason rather than replacing them with a different Claude model. Keep the AA benchmark report unchanged by account-specific availability.

For configuration files and commands, follow [Pi](pi.md) or [Oh My Pi](oh-my-pi.md). These instructions guide an authorised harness update; research-only runs must not change agent configuration.

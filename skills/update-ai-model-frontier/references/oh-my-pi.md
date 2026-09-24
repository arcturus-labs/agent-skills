# Oh My Pi (OMP) model setup

For direct Anthropic API access, also follow [Anthropic API setup](anthropic-api.md). Inspect credential precedence so an existing OAuth token does not silently replace the requested API-key route.

Use this reference when configuring `omp` from frontier results or matching a working Pi setup. The report scripts do not modify OMP. Prefer the installed version's help/schema; these notes were exercised with OMP 18.1.21. Official references: [models](https://github.com/can1357/oh-my-pi/blob/main/docs/models.md) and [providers](https://github.com/can1357/oh-my-pi/blob/main/docs/providers.md).

## Inspect and map

Run `omp --version`, `omp config path`, `omp models --help`, and inspect the selected profile's configuration. The usual user directory is `~/.omp/agent`, but profiles and overrides can change it. Inspect `config.yml`, any `models.yml`, and existing authentication without exposing secrets. For Pi parity, read Pi's current `models.json` and `settings.json` as the source of requested selections and defaults; do not freeze a historical model list in this skill.

Use `omp models --json` and `omp models find SEARCH` to check exact provider/model IDs before adding overrides. `omp models refresh` refreshes the catalogue, not the application. Prefer existing built-ins where they already match the intended route. A creator, inference host, and harness provider ID can differ. If the exact route is absent, verify an alternative host's exact model ID, credentials, and supported effort; disclose any routing/pricing difference. Do not substitute an aggregator for a direct provider without verifying the route and explaining the change.

## Register custom providers

Back up existing files before editing; preserve unrelated models, settings, and authentication. OMP uses YAML `models.yml`, with a top-level `providers` map. Do not copy Pi's JSON file verbatim. A minimal structural example (replace example values with verified values):

```yaml
providers:
  example-provider:
    baseUrl: https://api.example.com/v1
    api: openai-completions
    apiKey: EXAMPLE_API_KEY
    models:
      - id: verified-model-id
        name: Verified Model
        contextWindow: 128000
        maxTokens: 8192
        input: [text]
        reasoning: true
```

A bare environment-variable name in `apiKey` references the credential; ensure it is actually exported in the launch environment. OMP may interpret an unresolved string as a literal credential, so a missing variable is not solved by writing its name in YAML. Source the user's saved shell environment in the same invocation when needed. Never put literal keys in configuration examples or reports.

Port only verified model metadata, compatibility fields, and thinking mappings. Pi and OMP schemas differ. In OMP 18.1.21, `compat.thinkingFormat: deepseek` is invalid and disables **all** custom providers in the file. That version accepts `openai`, `openrouter`, `zai`, `qwen`, and `qwen-chat-template`. Using `openai` allowed the tested DeepSeek route to load and generate; this does not prove identical reasoning behavior across versions. Inspect the installed implementation/provider docs before translating compatibility flags, and verify the selected effort with the harness. Preserve provider-specific assistant reasoning-content requirements where supported. Do not treat a successful short reply as proof of benchmark-equivalent reasoning.

Meta may require a custom direct provider even when OpenRouter Meta models exist. Use the verified direct endpoint and environment variable; an example variable name is `META_AI_API_KEY`; match the user's configuration. DeepSeek commonly uses `DEEPSEEK_API_KEY`; Z.AI uses `ZAI_API_KEY`. Verify Z.AI Coding Plan versus general API endpoints for the user's account. These variable names do not imply that the user has credentials.

After editing, run the catalogue command and inspect stderr for schema warnings. A command can still list built-in models when the custom file failed validation. Confirm each intended custom provider/model actually appears.

## Apply selections and defaults

Use OMP's configuration interface, confirming syntax with `omp config --help`:

```sh
omp config get enabledModels --json
omp config get modelRoles --json
omp config get defaultThinkingLevel --json
omp config set enabledModels '["example-provider/verified-model-id:high"]'
```

The last command replaces the full list: construct the desired list from the user's requested scope and preserve existing selections unless replacement is requested. Keep `provider/model-id:effort` selectors and verify all selected thinking levels. Multiple effort entries for the same model are distinct selections.

OMP stores its default under `modelRoles.default`, not Pi's `defaultProvider` and `defaultModel`. To mirror Pi, translate those fields into a provider/model selector, optionally with the requested thinking suffix, and match `defaultThinkingLevel`. Read and merge the complete `modelRoles` object before setting it so other roles survive. Preserve the current default when the user only requests additional models.

`enabledModels` controls scoped selection/cycling; it does not remove OMP's bundled catalogue or prohibit access to other models. Keep the full catalogue unless the user explicitly requests a different policy.

## Verify and report

Check separately: configuration validity, exact catalogue registration, scoped selection, credential availability, and live generation. Compare every intended selector against `omp models --json` and supported effort metadata, then inspect the saved scope/default using `omp config get`. Start a fresh session to inspect the picker; catalogue registration alone does not prove scoped inclusion.

Use a minimal live request for newly added or repaired routes at their configured effort. Inspect `omp --help` for the installed version's options to disable tools and unrelated context/extensions; a baseline is:

```sh
omp --no-session --no-tools -p --model example-provider/verified-model-id --thinking high "Reply exactly MODEL_OK"
```

Test the resulting default without a model override if default resolution was changed. Existing OMP OAuth can satisfy Codex access; verify it before requesting login. Do not assume either that Pi's OAuth transfers or that OMP lacks its own login, and do not copy credential stores speculatively.

An `EPERM` creating an OMP runtime directory (such as beneath `~/.omp/run`) is a local filesystem permission failure before inference. Follow the environment's permission mechanism for the exact needed path. Do not rewrite provider credentials to fix it. Likewise, a Z.AI `429` with code `1113` and an insufficient-balance message is an account/resource failure; it is not evidence of a missing catalogue or invalid model definition. Report actual errors and stop repeated account/quota retries.

Summarize what was registered, selected, and live-tested, disclose alternate hosting routes and untested entries, and link the modified configuration and backup. Ask the user to restart an existing OMP session if needed to load changes.

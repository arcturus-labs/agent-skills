# Pi Claude bridge

Use this reference when the user wants Pi to run Claude through their Claude Code Pro or Max subscription rather than the direct Anthropic API. This route uses the `pi-claude-bridge` extension and selectors such as `claude-bridge/claude-sonnet-5`. The direct `anthropic/...` provider instead uses `ANTHROPIC_API_KEY` and is pay-as-you-go API billing.

## Subscription-only configuration

1. Confirm the extension is installed with `pi install npm:pi-claude-bridge`. It requires Pi 0.86.1 or newer. Refresh or start a fresh Pi process, then discover exact IDs with `pi --list-models claude-bridge`.
2. In `enabledModels`, use only verified `claude-bridge/MODEL_ID:EFFORT` entries for Claude. Remove every `anthropic/...` entry when the user requests a subscription-only model picker. Do not include both routes, since the picker alone does not communicate billing clearly.
3. Launch Pi without `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, or `ANTHROPIC_BASE_URL` in its environment. These variables can override the Claude Code child authentication. A safe launch is `env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u ANTHROPIC_BASE_URL pi`.
4. Ensure Claude Code itself is logged in to the intended Pro or Max account. The bridge consumes that subscription's Claude Code quota. It does not make usage unlimited, and Extra Usage can still be separately enabled by the user.
5. Verify the chosen selector appears in a fresh scoped picker and make one minimal request through `claude-bridge/...`. A catalog listing proves registration, not subscription authentication or quota.

For this strategy, use `high` for compact Claude families such as Haiku, `medium` for balanced families such as Sonnet, and `low` for flagship families such as Opus. Check the installed bridge catalogue before adding a new model, because supported effort levels can change.

Keep `ANTHROPIC_API_KEY` in secure shell storage if it is needed by other tools. The isolation requirement applies to the Pi process that uses the bridge. Do not delete keys or change the user's Claude plan merely to configure Pi.

If the user explicitly asks for direct API billing, reverse this policy only for that authorised change: select `anthropic/...`, load `ANTHROPIC_API_KEY`, and test that separate route. Do not silently fall back between bridge and direct API providers.

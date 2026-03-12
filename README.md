# OpenClaw 3.8 Kimi Code Patch Script

This is a last-resort patch script for **OpenClaw 2026.3.8** installations that fail with:

```text
Error: Config validation failed: models.providers.kimi-coding.models.0.compat: Unrecognized key: "requiresOpenAiAnthropicToolPayload"
```

## When to use this

Use this only if:

- you are **not comfortable rolling back** to another version, and
- you do **not want to run the current `main` source build** yet, even though the issue appears to be **resolved in source but not released**.

If you are comfortable with either of those options, they are cleaner than patching compiled release files.

## What this script does

`openclaw-patch-all.py`:

1. **Checks** which installed `dist/*.js` bundles still reference `requiresOpenAiAnthropicToolPayload` but do not allow it in `ModelCompatSchema`
2. **Backs up** every target file before changing anything
3. **Patches** those bundles by adding:

```js
requiresOpenAiAnthropicToolPayload: z.boolean().optional()
```

This brings the affected compiled bundles back in line with the source-level schema.

## What it does not do

- It does **not** rebuild OpenClaw from source
- It does **not** guarantee future upgrades will preserve the patch
- It does **not** address unrelated Kimi runtime issues beyond this schema mismatch

## Risks

- You are modifying **compiled release files** under your installed OpenClaw package, not changing the upstream source tree
- A future OpenClaw update or reinstall may overwrite the patch
- If OpenClaw 2026.3.8 on your machine has additional release-artifact inconsistencies, this script may fix this schema mismatch without fixing every related Kimi issue
- If your install path is different from `/opt/homebrew/lib/node_modules/openclaw/dist`, you must adjust the script before running it
- Although the script creates backups first, you should still review the target files it prints during the check phase before proceeding

## Requirements

- macOS or another environment where your OpenClaw install is under:
  - `/opt/homebrew/lib/node_modules/openclaw/dist`
- Python 3
- sudo access

## Usage

Run:

```bash
sudo python3 openclaw-patch-all.py
```

Then restart OpenClaw:

```bash
openclaw gateway restart
```

Then retry your original command.

## Backup location

The script creates timestamped backups under a path like:

```text
/Users/amber/openclaw-dist-backup-YYYYMMDD-HHMMSS
```

## Verify the patch

You can check whether multiple bundles now include the schema key with:

```bash
grep -RIn "requiresOpenAiAnthropicToolPayload: z.boolean().optional()" /opt/homebrew/lib/node_modules/openclaw/dist | sed -n '1,80p'
```

## Rollback

Restore the files you need from the backup directory created by the script, then restart the gateway.

## Why this exists

Current OpenClaw source appears to already include the schema fix in `src/config/zod-schema.core.ts`, but some released `dist` bundles in `2026.3.8` appear inconsistent: runtime code references `requiresOpenAiAnthropicToolPayload`, while some compiled schema bundles still reject it.

So this script is a temporary workaround for the released build, not a replacement for an upstream release.

from pathlib import Path
import shutil
from datetime import datetime

root = Path('/opt/homebrew/lib/node_modules/openclaw/dist')
needle = 'requiresMistralToolIds: z.boolean().optional()'
insert = needle + ',\n\trequiresOpenAiAnthropicToolPayload: z.boolean().optional()'
stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
backup_root = Path(f'/Users/amber/openclaw-dist-backup-{stamp}')

targets = []
skipped = []

for path in sorted(root.rglob('*.js')):
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        skipped.append((str(path), f'read failed: {e}'))
        continue

    if 'const ModelCompatSchema = z.object({' not in text:
        continue
    if '.requiresOpenAiAnthropicToolPayload === true' not in text and 'requiresOpenAiAnthropicToolPayload: true' not in text:
        continue
    if 'requiresOpenAiAnthropicToolPayload: z.boolean().optional()' in text:
        skipped.append((str(path), 'already patched'))
        continue
    if needle not in text:
        skipped.append((str(path), 'needle not found'))
        continue

    targets.append(path)

print('=== CHECK PHASE ===')
print(f'Found {len(targets)} file(s) to patch.\n')
for path in targets:
    print(path)

if skipped:
    print('\n=== SKIPPED ===')
    for p, reason in skipped:
        print(f'{p} :: {reason}')

if not targets:
    print('\nNothing to patch.')
    raise SystemExit(0)

print(f'\n=== BACKUP PHASE ===\nCreating backups under: {backup_root}')
for path in targets:
    rel = path.relative_to(root)
    dest = backup_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)

print('\n=== PATCH PHASE ===')
patched = []
for path in targets:
    text = path.read_text(encoding='utf-8', errors='ignore')
    new_text = text.replace(needle, insert, 1)
    if new_text != text:
        path.write_text(new_text, encoding='utf-8')
        patched.append(str(path))

for p in patched:
    print(p)

print(f'\nTotal patched: {len(patched)}')
print(f'Backup location: {backup_root}')

# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

#!/usr/bin/env bash
# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GIT_COMMON="$(git -C "$ROOT" rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
MAIN_REPO="$(dirname "$GIT_COMMON")"
[[ -n "$GIT_COMMON" && -d "$MAIN_REPO" ]] || MAIN_REPO="$ROOT"
_resolve_upstream() {
  local name="$1"
  local var="${2:-}"
  if [[ -n "$var" && -d "$var" ]]; then
    echo "$var"
    return
  fi
  for candidate in "$ROOT/../$name" "$MAIN_REPO/../$name"; do
    if [[ -d "$candidate" ]]; then
      cd "$candidate" && pwd
      return
    fi
  done
  echo ""
}
METAGPT_SRC="$(_resolve_upstream MetaGPT "${METAGPT_SRC:-}")"
AGENCY_SRC="$(_resolve_upstream agency-agents "${AGENCY_SRC:-}")"

if [[ -z "$METAGPT_SRC" || ! -d "$METAGPT_SRC" ]]; then
  echo "error: MetaGPT source not found. Set METAGPT_SRC." >&2
  exit 1
fi
if [[ -z "$AGENCY_SRC" || ! -d "$AGENCY_SRC" ]]; then
  echo "error: agency-agents source not found. Set AGENCY_SRC." >&2
  exit 1
fi

METAGPT_SHA="$(git -C "$METAGPT_SRC" rev-parse HEAD)"
AGENCY_SHA="$(git -C "$AGENCY_SRC" rev-parse HEAD)"

echo "Syncing MetaGPT ($METAGPT_SHA)"
rm -rf "$ROOT/vendor/MetaGPT"
mkdir -p "$ROOT/vendor"
rsync -a --delete \
  --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
  --exclude '.pytest_cache' --exclude 'workspace' \
  --exclude '*.egg-info' \
  "$METAGPT_SRC/" "$ROOT/vendor/MetaGPT/"

echo "Syncing agency-agents ($AGENCY_SHA)"
rm -rf "$ROOT/vendor/agency-agents"
rsync -a --delete \
  --exclude '.git' --exclude 'info-sentry' --exclude '__pycache__' \
  --exclude '*.egg-info' \
  "$AGENCY_SRC/" "$ROOT/vendor/agency-agents/"
rm -rf "$ROOT/vendor/agency-agents/info-sentry"

if [[ -d "$ROOT/vendor/agency-agents/info-sentry" ]]; then
  echo "error: info-sentry present after sync" >&2
  exit 1
fi

for lic in "$ROOT/vendor/MetaGPT/LICENSE" "$ROOT/vendor/agency-agents/LICENSE"; do
  [[ -f "$lic" ]] || { echo "missing $lic" >&2; exit 1; }
  head -5 "$lic" | grep -qiE 'MIT|Permission' || { echo "bad license $lic" >&2; exit 1; }
done

cat > "$ROOT/vendor/UPDATE.md" <<EOF
# Vendored upstream versions

| Package | SHA | Synced |
|---------|-----|--------|
| MetaGPT | \`${METAGPT_SHA}\` | $(date -u +"%Y-%m-%dT%H:%MZ") |
| agency-agents | \`${AGENCY_SHA}\` | $(date -u +"%Y-%m-%dT%H:%MZ") |

## Re-vendor

\`\`\`bash
make vendor-sync
\`\`\`

Override sources: \`METAGPT_SRC\`, \`AGENCY_SRC\`.

## Internal note

\`info-sentry/\` is excluded at vendor time as out-of-scope upstream content.
EOF

echo "Done. MetaGPT=$METAGPT_SHA agency-agents=$AGENCY_SHA"

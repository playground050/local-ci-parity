#!/usr/bin/env bash
# Publish a Markdown doc to dev.to, or update the article if it already exists.
#
# The first H1 becomes the title and is removed from the body. The article is
# matched by canonical_url, so no article id has to be stored anywhere.
# A new article is created as a draft. An existing article keeps its current
# published state, so publishing it on dev.to by hand is never undone here.
#
# Required env: DOC, CANONICAL_URL, TAGS, DESCRIPTION
# Without DEVTO_API_KEY (and DRY_RUN unset) it warns and exits 0.
set -euo pipefail

: "${DOC:?}" "${CANONICAL_URL:?}" "${TAGS:?}" "${DESCRIPTION:?}"
DRY_RUN="${DRY_RUN:-false}"
API="${DEVTO_API_URL:-https://dev.to/api}"
ACCEPT='accept: application/vnd.forem.api-v1+json'

title=$(grep -m1 '^# ' "$DOC" | sed 's/^# //')
[ -n "$title" ] || { echo "no H1 title in $DOC" >&2; exit 1; }
body=$(awk 'done || !/^# / {print; next} {done=1}' "$DOC" | sed '/./,$!d')

api() {
  curl --fail-with-body -sS -H "api-key: ${DEVTO_API_KEY}" -H "$ACCEPT" \
    -H 'content-type: application/json' "$@"
}

id=""
published=false
if [ "$DRY_RUN" != true ] && [ -z "${DEVTO_API_KEY:-}" ]; then
  echo "::warning::DEVTO_API_KEY is not set; skipping the dev.to publish"
  exit 0
fi
if [ "$DRY_RUN" != true ]; then
  page=1
  while :; do
    list=$(api "$API/articles/me/all?per_page=1000&page=$page")
    [ "$(jq length <<<"$list")" -gt 0 ] || break
    hit=$(jq -c --arg u "$CANONICAL_URL" 'map(select(.canonical_url == $u)) | first // empty' <<<"$list")
    if [ -n "$hit" ]; then
      id=$(jq -r .id <<<"$hit")
      published=$(jq -r .published <<<"$hit")
      break
    fi
    [ "$(jq length <<<"$list")" -eq 1000 ] || break
    page=$((page + 1))
  done
fi

# JSON strings are valid YAML scalars, so jq quotes the front matter values.
q() { jq -Rn --arg v "$1" '$v'; }
markdown=$(printf -- '---\ntitle: %s\npublished: %s\ndescription: %s\ntags: %s\ncanonical_url: %s\n---\n\n%s\n' \
  "$(q "$title")" "$published" "$(q "$DESCRIPTION")" "$TAGS" "$(q "$CANONICAL_URL")" "$body")
payload=$(jq -n --arg md "$markdown" '{article: {body_markdown: $md}}')

if [ "$DRY_RUN" = true ]; then
  echo "dry run: would create a draft (an existing article would be updated in place)"
  printf '%s\n' "$markdown" | head -n 12
  echo "... ($(printf '%s' "$markdown" | wc -l) lines)"
  exit 0
fi

if [ -n "$id" ]; then
  res=$(api -X PUT "$API/articles/$id" --data "$payload")
  action="updated (published: $published)"
else
  res=$(api -X POST "$API/articles" --data "$payload")
  action="created as a draft"
fi
url=$(jq -r .url <<<"$res")
echo "$action: $url"
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  echo "dev.to article $action: $url" >>"$GITHUB_STEP_SUMMARY"
fi

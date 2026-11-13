#!/bin/sh
set -e
out="${1:?usage: download.sh <folder>}"
tail -n +2 "$(dirname "$0")/SOURCES.tsv" | while IFS="$(printf '\t')" read -r t suite model file sha bytes url; do
  mkdir -p "$out/$model"
  curl -s -f -o "$out/$model/$file" "$url"
  got=$(shasum -a 256 "$out/$model/$file" | cut -c1-64)
  [ "$got" = "$sha" ] || { echo "hash mismatch: $model/$file"; exit 1; }
  echo "ok $model/$file"
done

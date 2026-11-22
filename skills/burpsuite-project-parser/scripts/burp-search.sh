#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: burp-search.sh <project.burp> [arguments...]" >&2
  exit 2
fi

project=$1
shift

: "${BURP_JAVA:?Set BURP_JAVA to the Java executable}"
: "${BURP_JAR:?Set BURP_JAR to burpsuite_pro.jar}"

[[ -r "$project" ]] || { echo "project not readable: $project" >&2; exit 2; }
[[ -x "$BURP_JAVA" ]] || { echo "Java not executable: $BURP_JAVA" >&2; exit 2; }
[[ -r "$BURP_JAR" ]] || { echo "Burp JAR not readable: $BURP_JAR" >&2; exit 2; }

exec "$BURP_JAVA" -Djava.awt.headless=true -jar "$BURP_JAR"   --project-file="$project" "$@"

#!/usr/bin/env bash
# PostToolUse(Write/Edit): ejecuta el formatter del proyecto según el tipo de archivo.
# Lee tool_input.file_path de stdin (JSON). No bloquea — solo formatea. (Sintesis.md §10)
#
# HIGH-7 fix: glob expansion con compgen para detectar configs de eslint.
# HIGH-8: añadidos formatters Java/Kotlin/C++/Dart/Swift/Perl.

set -euo pipefail

INPUT=$(cat /dev/stdin)
FILE_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
    echo '{"decision":"allow","reason":"auto-format: sin file_path"}'
    exit 0
fi

# Helper: ejecuta un comando si existe, devuelve OK/skip
run_or_skip() {
    local label="$1"
    shift
    if command -v "$1" >/dev/null 2>&1; then
        "$@" 2>/dev/null || true
        echo "{\"decision\":\"allow\",\"reason\":\"auto-format: ${label} ejecutado\"}"
    else
        echo "{\"decision\":\"allow\",\"reason\":\"auto-format: ${label} no instalado, skip\"}"
    fi
}

# Detectar tipo de archivo y ejecutar formatter apropiado
case "$FILE_PATH" in
    *.php)
        if [ -x ./vendor/bin/pint ]; then
            ./vendor/bin/pint "$FILE_PATH" --quiet 2>/dev/null || true
            echo '{"decision":"allow","reason":"auto-format: pint ejecutado"}'
        else
            echo '{"decision":"allow","reason":"auto-format: pint no instalado, skip"}'
        fi
        ;;
    *.py)
        run_or_skip "ruff" ruff format "$FILE_PATH" --quiet
        ;;
    *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs)
        if command -v npx >/dev/null 2>&1 && \
           { compgen -G ".eslintrc*" >/dev/null || compgen -G "eslint.config.*" >/dev/null; }; then
            npx eslint "$FILE_PATH" --fix --quiet 2>/dev/null || true
            echo '{"decision":"allow","reason":"auto-format: eslint --fix ejecutado"}'
        elif command -v prettier >/dev/null 2>&1; then
            prettier --write "$FILE_PATH" 2>/dev/null || true
            echo '{"decision":"allow","reason":"auto-format: prettier ejecutado"}'
        else
            echo '{"decision":"allow","reason":"auto-format: eslint/prettier no disponible, skip"}'
        fi
        ;;
    *.go)
        run_or_skip "gofmt" gofmt -w "$FILE_PATH"
        ;;
    *.rs)
        run_or_skip "rustfmt" rustfmt "$FILE_PATH"
        ;;
    *.java)
        if command -v google-java-format >/dev/null 2>&1; then
            google-java-format -i "$FILE_PATH" 2>/dev/null || true
            echo '{"decision":"allow","reason":"auto-format: google-java-format ejecutado"}'
        elif [ -f "./gradlew" ] && grep -q "spotless" build.gradle* 2>/dev/null; then
            ./gradlew spotlessApply --quiet 2>/dev/null || true
            echo '{"decision":"allow","reason":"auto-format: spotlessApply ejecutado"}'
        else
            echo '{"decision":"allow","reason":"auto-format: java formatter no disponible, skip"}'
        fi
        ;;
    *.kt|*.kts)
        run_or_skip "ktlint" ktlint --format "$FILE_PATH"
        ;;
    *.cpp|*.cxx|*.cc|*.h|*.hpp|*.hxx)
        run_or_skip "clang-format" clang-format -i "$FILE_PATH"
        ;;
    *.dart)
        run_or_skip "dart" dart format "$FILE_PATH"
        ;;
    *.swift)
        run_or_skip "swift-format" swift-format format -i "$FILE_PATH"
        ;;
    *.pl|*.pm|*.t)
        run_or_skip "perltidy" perltidy -b "$FILE_PATH"
        ;;
    *.rb)
        run_or_skip "rubocop" rubocop -a "$FILE_PATH" --quiet
        ;;
    *.cs)
        run_or_skip "dotnet" dotnet format --include "$FILE_PATH"
        ;;
    *.sh|*.bash)
        run_or_skip "shfmt" shfmt -w "$FILE_PATH"
        ;;
    *.json)
        if command -v jq >/dev/null 2>&1; then
            tmp=$(mktemp)
            jq . "$FILE_PATH" > "$tmp" 2>/dev/null && mv "$tmp" "$FILE_PATH" || rm -f "$tmp"
            echo '{"decision":"allow","reason":"auto-format: jq ejecutado"}'
        else
            echo '{"decision":"allow","reason":"auto-format: jq no instalado, skip"}'
        fi
        ;;
    *)
        echo '{"decision":"allow","reason":"auto-format: tipo de archivo sin formatter configurado"}'
        ;;
esac

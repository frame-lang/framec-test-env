# Source-hash cache for `framec compile`.
# Usage (sourced by every *_batch.sh):
#   . /framec_cached.sh
#   framec_cached <target_lang> <out_dir> <source.f*> [err_file]
#
# Returns 0 on success (cache hit or successful transpile + cache populated),
# non-zero if framec itself fails (cache is NOT populated on failure).
# Cache entries are tars of the out_dir contents; restore via tar -x.
#
# Keying: (framec binary sha256, target lang, source file sha256).
# The framec hash is computed once per container invocation and memoised.

: "${FRAMEC_BIN:=$(command -v framec 2>/dev/null)}"
_FRAMEC_HASH_FILE="/tmp/.framec_version_hash"
if [ -n "${FRAMEC_BIN}" ] && { [ ! -f "$_FRAMEC_HASH_FILE" ] || [ "$FRAMEC_BIN" -nt "$_FRAMEC_HASH_FILE" ]; }; then
    sha256sum "$FRAMEC_BIN" 2>/dev/null | cut -d' ' -f1 | cut -c1-16 > "$_FRAMEC_HASH_FILE"
fi
FRAMEC_HASH=$(cat "$_FRAMEC_HASH_FILE" 2>/dev/null || echo unknown)
_CACHE_ROOT="${FRAMEC_CACHE_DIR:-/output/.framec_cache}/${FRAMEC_HASH}"
mkdir -p "$_CACHE_ROOT"

framec_cached() {
    local target="$1"
    local out_dir="$2"
    local src_file="$3"
    local err_file="${4:-/tmp/compile_err}"
    local key cache_path
    key=$(sha256sum "$src_file" 2>/dev/null | cut -d' ' -f1)
    if [ -z "$key" ]; then
        # No hash — fall through to framec; cache disabled for this row.
        framec compile -l "$target" -o "$out_dir" "$src_file" >/dev/null 2>"$err_file"
        return $?
    fi
    cache_path="$_CACHE_ROOT/${target}/${key}.tar"
    if [ -f "$cache_path" ]; then
        mkdir -p "$out_dir"
        if tar -xf "$cache_path" -C "$out_dir" 2>/dev/null; then
            : > "$err_file"
            return 0
        fi
        # Corrupted cache entry; fall through.
        rm -f "$cache_path"
    fi
    if framec compile -l "$target" -o "$out_dir" "$src_file" >/dev/null 2>"$err_file"; then
        mkdir -p "$(dirname "$cache_path")"
        ( cd "$out_dir" && tar -cf "${cache_path}.tmp" . 2>/dev/null ) \
            && mv "${cache_path}.tmp" "$cache_path" \
            || rm -f "${cache_path}.tmp"
        return 0
    fi
    return 1
}

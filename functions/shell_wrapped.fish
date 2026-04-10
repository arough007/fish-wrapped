function shell_wrapped --description "Shell Wrapped - your year in the terminal"
    set -l script ~/.config/fish/functions/shell_wrapped.py

    # Dismiss the January hint without running the report
    if test (count $argv) -eq 1; and test "$argv[1]" = "--dismiss"
        set -l last_year (math (date +%Y) - 1)
        touch ~/.local/share/shell-track/wrapped_seen_$last_year
        echo "Dismissed. Run 'shell_wrapped $last_year' whenever you're ready."
        return 0
    end

    if not test -f $script
        echo "shell_wrapped: script not found at $script" >&2
        echo "Try reinstalling the plugin: fisher install arough007/fish-wrapped" >&2
        return 1
    end

    # Mark the hint as seen for last year
    set -l last_year (math (date +%Y) - 1)
    touch ~/.local/share/shell-track/wrapped_seen_$last_year

    if command -q uv
        uv run $script $argv
    else if command -q python3
        python3 $script $argv
    else
        echo "shell_wrapped: requires uv or python3 — https://docs.astral.sh/uv/" >&2
        return 1
    end
end

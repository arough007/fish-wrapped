function shell_wrapped --description "Shell Wrapped - your year in the terminal"
    set -l script ~/.config/fish/functions/shell_wrapped.py

    if not test -f $script
        echo "shell_wrapped: script not found at $script" >&2
        echo "Try reinstalling the plugin: fisher install <your-username>/fish-wrapped" >&2
        return 1
    end

    if command -q uv
        uv run $script $argv
    else
        python3 $script $argv
    end
end

function __shell_wrapped_install --on-event fisher_install --on-event fisher_update
    for plugin in $argv
        if string match -q "*fish-wrapped*" $plugin
            mkdir -p ~/.local/share/shell-track
            cp $plugin/shell_wrapped.py ~/.local/share/shell-track/shell_wrapped.py
            echo "shell_wrapped: installed shell_wrapped.py to ~/.local/share/shell-track/"
        end
    end
end

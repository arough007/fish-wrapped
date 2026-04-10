# Shell tracking for detailed command history
# Logs every command execution with timestamp, duration, exit code, directory, and command
# Install: cp shell_track.fish ~/.config/fish/functions/shell_track.fish

function __shell_track_init --on-event fish_greeting
    mkdir -p ~/.local/share/shell-track
end

function __shell_track_pre --on-event fish_preexec
    set -g __shell_track_start (perl -MTime::HiRes=time -e 'printf "%.0f\n", time()*1000')
end

function __shell_track_post --on-event fish_postexec
    set -l exit_code $status
    set -l end_time (perl -MTime::HiRes=time -e 'printf "%.0f\n", time()*1000')
    set -l duration 0

    if set -q __shell_track_start
        set duration (math "$end_time - $__shell_track_start")
    end

    set -l cmd (string replace --all -- \n \\n $argv[1])
    set -l pwd_path $PWD
    set -l timestamp (math -s0 "$end_time / 1000")

    set -l log_dir ~/.local/share/shell-track

    # Log format: timestamp_s|duration_ms|exit_code|pwd|cmd
    echo "$timestamp|$duration|$exit_code|$pwd_path|$cmd" >> $log_dir/history.log
    set -e __shell_track_start
end

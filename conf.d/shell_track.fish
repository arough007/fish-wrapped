# Shell tracking for detailed command history
# Logs every command execution with timestamp, duration, exit code, directory, and command

# Only run for interactive shells — skip for scripts and `fish -c ...`
if not status is-interactive
    return
end

# Run at shell startup (conf.d is sourced when fish starts)
mkdir -p ~/.local/share/shell-track

if not command -q perl
    echo "shell-track: perl not found — command tracking disabled" >&2
    set -g __shell_track_disabled 1
end

# January reminder to run Shell Wrapped for last year
set -l __shell_track_month (date +%m)
set -l __shell_track_last_year (math (date +%Y) - 1)
if test "$__shell_track_month" = "01"; and not test -f ~/.local/share/shell-track/wrapped_seen_$__shell_track_last_year
    echo "🎉 It's a new year! Run 'shell_wrapped "$__shell_track_last_year"0101 "$__shell_track_last_year"1231' to see your $__shell_track_last_year Shell Wrapped."
    echo "   (Run 'shell_wrapped --dismiss' to hide this)"
end
set -e __shell_track_month __shell_track_last_year

function __shell_track_pre --on-event fish_preexec
    set -q __shell_track_disabled; and return
    set -g __shell_track_start (perl -MTime::HiRes=time -e 'printf "%.0f\n", time()*1000')
end

function __shell_track_post --on-event fish_postexec
    set -l exit_code $status  # capture before anything else changes $status
    set -q __shell_track_disabled; and return
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

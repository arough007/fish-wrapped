# fish-wrapped

A fish shell plugin that tracks every command you run and generates a Spotify Wrapped–style year-in-review report for your terminal.

```
╔══════════════════════════════════════════════╗
║    🎉   Your 2026 Shell Wrapped   🎉         ║
╚══════════════════════════════════════════════╝

📊 VOLUME
  → 4,821 commands executed
  → Average 93 commands/day
  → vs prev period (Dec 01 – Dec 31 2025): ↑ 12% (+514)

🏆 TOP COMMANDS
   1. git    1,047x  ↑ 8%   22% of all
   2. cd       631x  ↑ 3%   13% of all
   3. ls       580x  ↓ 5%   12% of all
   ...

🕐 TIME PATTERNS
  → Busiest month:    Mar  (621 commands)
  → Most productive:  Wednesday
  → Most active hour: 10am
  → Weekend warrior:  14.2% of commands on weekends
  → Early bird 🌅:    3.1% before 9am
  → Night owl 🦉:     8.7% after 10pm

📁 WORKSPACE
  → Most worked directory:
    ~/git/my-project  (1,203 commands)

✅ SUCCESS RATE
  → 94.3% of commands succeeded
  → ✓ 4,547 succeeded   ✗ 274 failed

⏱️  DURATION STATS
  → Speed demon:     3,901 commands under 1 second
  → Marathon runner: 12 commands over 5 minutes
  → Longest: 47m  docker build --no-cache .

🎮 FUN STATS
  → Longest streak:    38 consecutive days 🔥
  → Command diversity: 312 unique commands
  → Longest command:   284 characters
```

## Requirements

- [fish](https://fishshell.com/) 3.6+
- `perl` with `Time::HiRes` (standard on macOS and most Linux distros)
- [`uv`](https://docs.astral.sh/uv/) (recommended) **or** `python3` with `pip install rich`

## Installation

### With [Fisher](https://github.com/jorgebucaran/fisher)

```fish
fisher install arough007/fish-wrapped
```

### Manually

```fish
curl -sL https://raw.githubusercontent.com/arough007/fish-wrapped/master/conf.d/shell_track.fish \
  > ~/.config/fish/conf.d/shell_track.fish

curl -sL https://raw.githubusercontent.com/arough007/fish-wrapped/master/functions/shell_wrapped.fish \
  > ~/.config/fish/functions/shell_wrapped.fish

curl -sL https://raw.githubusercontent.com/arough007/fish-wrapped/master/functions/shell_wrapped.py \
  > ~/.config/fish/functions/shell_wrapped.py
```

## Usage

Once installed, every command you run is silently logged. To generate your report:

```fish
shell_wrapped
```

By default this covers January 1 of the current year through today. You can pass a custom date range:

```fish
shell_wrapped 20260101 20260630   # first half of 2026
shell_wrapped 20250101 20251231   # full year 2025
```

Each section compares your current period against the equivalent previous period (e.g. last year, or the same number of days immediately before the start date).

The **Success Rate** and **Duration Stats** sections only appear when using shell-track data (not fish's built-in history), since fish history doesn't record exit codes or timings.

## How it works

`conf.d/shell_track.fish` hooks into fish's `fish_preexec` / `fish_postexec` events and appends one line per command to:

```
~/.local/share/shell-track/history.log
```

Log format:

```
timestamp_s|duration_ms|exit_code|pwd|cmd
```

`shell_wrapped` reads this log (falling back to fish's built-in history at `~/.local/share/fish/fish_history` if the log is missing) and renders the report using [Rich](https://github.com/Textualize/rich).

## License

[MIT](LICENSE)

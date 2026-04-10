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
  → Most frustrating: npm (12 failures)

⏱️  DURATION STATS
  → Speed demon:     3,901 commands under 1 second
  → Marathon runner: 12 commands over 5 minutes
  → Longest: 47m  docker build --no-cache .

🎮 FUN STATS
  → Longest streak:    38 consecutive days 🔥
  → Command diversity: 312 unique commands
  → Longest command:   284 characters
```

## Why fish-wrapped?

Fish's built-in history only records the command text and a timestamp. fish-wrapped's custom tracker adds three things fish doesn't capture:

| | fish history | fish-wrapped |
|---|:---:|:---:|
| Command text | ✅ | ✅ |
| Timestamp | ✅ | ✅ |
| **Duration** | ❌ | ✅ |
| **Exit code** | ❌ | ✅ |
| **Working directory** | ❌ | ✅ |

That extra data unlocks the **Success Rate**, **Duration Stats**, and **Workspace** sections of the report, and makes everything else more accurate. It also enables year-over-year comparisons — every section shows a delta against the equivalent previous period, so you see not just what you did but whether you're doing more or less of it than before.

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
shell_wrapped          # current year, Jan 1 through today
shell_wrapped 2025     # full calendar year 2025
shell_wrapped 20260101 20260630   # any custom date range
```

Each section compares your current period against the equivalent previous period, so you can see trends over time.

The **Success Rate**, **Duration Stats**, and **Workspace** sections require shell-track data, since fish's built-in history doesn't record exit codes, timings, or working directories.

### A note on fish's built-in history

fish-wrapped does not fall back to fish's built-in history. Fish history only stores the *most recent* invocation of each unique command, not every run — so importing it would make volume counts, top command rankings, time patterns, and streaks all incorrect. Data collection starts from the moment the plugin is installed. After a week or two of normal use the report becomes meaningful; after a full year it's great.

### January reminder

In January, opening a new shell shows:

```
🎉 It's a new year! Run 'shell_wrapped 2025' to see your 2025 Shell Wrapped.
   (Run 'shell_wrapped --dismiss' to hide this)
```

It appears on every new shell in January until you either run `shell_wrapped` or `shell_wrapped --dismiss`, after which it's suppressed for the rest of the year.

## How it works

`conf.d/shell_track.fish` hooks into fish's `fish_preexec` / `fish_postexec` events and appends one line per command to:

```
~/.local/share/shell-track/history.log
```

Log format:

```
timestamp_s|duration_ms|exit_code|pwd|cmd
```

`shell_wrapped` reads this log and renders the report using [Rich](https://github.com/Textualize/rich).

## License

[MIT](LICENSE)

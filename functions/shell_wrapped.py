# /// script
# requires-python = ">=3.11"
# dependencies = ["rich"]
# ///

"""🎉 Shell Wrapped - Your year in the terminal"""

import argparse
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    print("shell_wrapped: 'rich' is not installed.", file=sys.stderr)
    print("  Best fix:  install uv and it will be handled automatically", file=sys.stderr)
    print("             https://docs.astral.sh/uv/getting-started/installation/", file=sys.stderr)
    print("  Quick fix: pip install rich", file=sys.stderr)
    sys.exit(1)

console = Console()

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_date(s: str) -> datetime:
    """Parse a date string in YYYYMMDD format."""
    try:
        return datetime.strptime(s, "%Y%m%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date '{s}' — expected YYYYMMDD (e.g. 20250101)")


def parse_shell_track(log_path: Path) -> list[dict]:
    """Parse shell-track log: timestamp_s|duration_ms|exit_code|pwd|cmd"""
    entries = []
    with open(log_path, errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 4)
            if len(parts) < 5:
                continue
            try:
                ts, duration_ms, exit_code, pwd, cmd = parts
                if not ts:
                    continue
                entries.append({
                    "timestamp": int(float(ts)),
                    "duration_ms": int(float(duration_ms)) if duration_ms else None,
                    "exit_code": int(exit_code) if exit_code else None,
                    "pwd": pwd,
                    "cmd": cmd.replace("\\n", "\n"),
                })
            except ValueError:
                continue
    return entries


def parse_fish_history(history_path: Path) -> list[dict]:
    """Parse fish history YAML-like format"""
    entries = []
    current_cmd = None
    current_when = None
    current_paths: list[str] = []
    in_paths = False

    with open(history_path, errors="replace") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("- cmd:"):
                if current_cmd and current_when:
                    entries.append({
                        "timestamp": current_when,
                        "duration_ms": None,
                        "exit_code": None,
                        "pwd": current_paths[0] if current_paths else None,
                        "cmd": current_cmd,
                    })
                current_cmd = line[len("- cmd:"):].strip()
                current_when = None
                current_paths = []
                in_paths = False
            elif line.startswith("  when:"):
                try:
                    current_when = int(line[len("  when:"):].strip())
                except ValueError:
                    pass
                in_paths = False
            elif line.startswith("  paths:"):
                in_paths = True
            elif line.startswith("    - ") and in_paths:
                current_paths.append(line.strip()[2:])
            else:
                in_paths = False

    if current_cmd and current_when:
        entries.append({
            "timestamp": current_when,
            "duration_ms": None,
            "exit_code": None,
            "pwd": current_paths[0] if current_paths else None,
            "cmd": current_cmd,
        })

    return entries


def load_entries() -> tuple[list[dict], str]:
    shell_track_log = Path.home() / ".local/share/shell-track/history.log"
    fish_history = Path.home() / ".local/share/fish/fish_history"

    if shell_track_log.exists():
        return parse_shell_track(shell_track_log), f"shell-track ({shell_track_log})"
    elif fish_history.exists():
        return parse_fish_history(fish_history), f"fish history ({fish_history})"
    else:
        console.print("[red]No history file found.[/red]")
        console.print("[dim]Expected: ~/.local/share/shell-track/history.log or ~/.local/share/fish/fish_history[/dim]")
        sys.exit(1)


def yoy(current: int, previous: int) -> str:
    if previous == 0:
        return "[dim]n/a[/dim]"
    pct = ((current - previous) / previous) * 100
    sign = "+" if pct >= 0 else ""
    color = "green" if pct >= 0 else "red"
    return f"[{color}]{sign}{pct:.1f}%[/{color}]"


def fmt_hour(hour: int) -> str:
    if hour == 0:
        return "12:00 AM"
    elif hour < 12:
        return f"{hour}:00 AM"
    elif hour == 12:
        return "12:00 PM"
    else:
        return f"{hour - 12}:00 PM"


def section(icon: str, title: str, color: str) -> Text:
    t = Text()
    t.append(f"{icon} ", style="bold")
    t.append(title, style=f"bold {color}")
    return t


def main():
    # Allow `shell_wrapped 2025` as shorthand for `shell_wrapped 20250101 20251231`
    if len(sys.argv) == 2 and re.fullmatch(r"\d{4}", sys.argv[1]):
        year = sys.argv[1]
        sys.argv[1:] = [f"{year}0101", f"{year}1231"]

    parser = argparse.ArgumentParser(description="Shell Wrapped — your terminal in review")
    parser.add_argument(
        "start",
        nargs="?",
        type=parse_date,
        default=datetime(datetime.now().year, 1, 1),
        metavar="YYYYMMDD",
        help="Start date (default: Jan 1 of current year). Pass a 4-digit year (e.g. 2025) to cover the full year.",
    )
    parser.add_argument(
        "end",
        nargs="?",
        type=parse_date,
        default=datetime.now(),
        metavar="YYYYMMDD",
        help="End date inclusive (default: today)",
    )
    args = parser.parse_args()

    start_dt: datetime = args.start
    end_dt: datetime = args.end.replace(hour=23, minute=59, second=59)

    if start_dt > end_dt:
        console.print("[red]Error: start date must be before end date.[/red]")
        sys.exit(1)

    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())

    # Previous period: same length, immediately before start
    period_days = (end_dt.date() - start_dt.date()).days + 1
    prev_end_dt = start_dt - timedelta(days=1)
    prev_start_dt = prev_end_dt - timedelta(days=period_days - 1)
    prev_start_ts = int(prev_start_dt.timestamp())
    prev_end_ts = int(prev_end_dt.replace(hour=23, minute=59, second=59).timestamp())

    all_entries, source = load_entries()
    console.print(f"[dim]Source: {source}[/dim]")
    console.print(f"[dim]Total entries in file: {len(all_entries):,}[/dim]")
    console.print()

    entries = [e for e in all_entries if start_ts <= e["timestamp"] <= end_ts]
    prev_entries = [e for e in all_entries if prev_start_ts <= e["timestamp"] <= prev_end_ts]

    if not entries:
        console.print(f"[red]No entries found between {start_dt.strftime('%Y-%m-%d')} and {end_dt.strftime('%Y-%m-%d')}.[/red]")
        sys.exit(1)

    total = len(entries)
    total_prev = len(prev_entries)
    days_elapsed = period_days
    avg_per_day = total / days_elapsed

    # Commands
    cmds = [e["cmd"].split()[0] for e in entries if e["cmd"].strip()]
    cmds_prev = [e["cmd"].split()[0] for e in prev_entries if e["cmd"].strip()]
    counter = Counter(cmds)
    counter_prev = Counter(cmds_prev)
    top_10 = [(cmd, count) for cmd, count in counter.most_common(11) if cmd][:10]

    # Time patterns
    dts = [datetime.fromtimestamp(e["timestamp"]) for e in entries]
    months = Counter(dt.month for dt in dts)
    weekdays = Counter(dt.weekday() for dt in dts)
    hours = Counter(dt.hour for dt in dts)
    busiest_month = max(months, key=months.get)
    most_productive_day = max(weekdays, key=weekdays.get)
    peak_hour = max(hours, key=hours.get)
    weekend_pct = sum(v for k, v in weekdays.items() if k >= 5) / total * 100
    early_bird_pct = sum(v for k, v in hours.items() if k < 9) / total * 100
    night_owl_pct = sum(v for k, v in hours.items() if k >= 22) / total * 100

    # Workspace
    pwd_counts = Counter(
        e["pwd"] for e in entries
        if e["pwd"] and e["pwd"] not in ("None", "")
    )
    most_worked_dir = pwd_counts.most_common(1)[0] if pwd_counts else None

    # Fun stats
    unique_days = sorted(set(dt.date() for dt in dts))
    longest_streak = cur_streak = 1
    for i in range(1, len(unique_days)):
        if (unique_days[i] - unique_days[i - 1]).days == 1:
            cur_streak += 1
            longest_streak = max(longest_streak, cur_streak)
        else:
            cur_streak = 1

    unique_cmds = len(counter)
    longest_cmd_entry = max(entries, key=lambda e: len(e["cmd"]))
    longest_cmd_preview = (
        longest_cmd_entry["cmd"][:60] + "..."
        if len(longest_cmd_entry["cmd"]) > 60
        else longest_cmd_entry["cmd"]
    )

    # Optional sections (only with shell-track data)
    has_exit_codes = any(e["exit_code"] is not None for e in entries)
    has_durations = any(e["duration_ms"] is not None for e in entries)

    # --- Output ---
    # Build title: show year if range is a full year, otherwise show date range
    if start_dt.month == 1 and start_dt.day == 1 and end_dt.month == 12 and end_dt.day == 31 and start_dt.year == end_dt.year:
        title = f"🎉   Your {start_dt.year} Shell Wrapped   🎉"
    else:
        title = f"🎉   Shell Wrapped  {start_dt.strftime('%b %d %Y')} → {end_dt.strftime('%b %d %Y')}   🎉"

    console.print(Panel(
        Text(title, justify="center", style="bold magenta"),
        box=box.DOUBLE,
        border_style="magenta",
        padding=(0, 4),
    ))
    console.print()

    # VOLUME
    console.print(section("📊", "VOLUME", "blue"))
    console.print(f"  → [bold]{total:,}[/bold] commands executed")
    console.print(f"  → Average [bold]{avg_per_day:.0f}[/bold] commands/day")
    diff = total - total_prev
    sign = "+" if diff >= 0 else ""
    prev_label = f"{prev_start_dt.strftime('%b %d')} – {prev_end_dt.strftime('%b %d %Y')}"
    console.print(f"  → vs prev period [dim]({prev_label})[/dim]: {yoy(total, total_prev)} ([dim]{sign}{diff:,}[/dim])")
    console.print()

    # TOP COMMANDS
    console.print(section("🏆", "TOP COMMANDS", "yellow"))
    for i, (cmd, count) in enumerate(top_10, 1):
        pct = count / total * 100
        prev_count = counter_prev.get(cmd, 0)
        console.print(
            f"  {i:>2}. [bold cyan]{cmd}[/bold cyan]"
            f"  [white]{count:,}x[/white]"
            f"  {yoy(count, prev_count)}"
            f"  [dim]{pct:.0f}% of all[/dim]"
        )
    console.print()

    # TIME PATTERNS
    console.print(section("🕐", "TIME PATTERNS", "cyan"))
    console.print(f"  → Busiest month:      [bold]{MONTHS[busiest_month - 1]}[/bold]  [dim]({months[busiest_month]:,} commands)[/dim]")
    console.print(f"  → Most productive:    [bold]{DAYS[most_productive_day]}[/bold]")
    console.print(f"  → Most active hour:   [bold]{fmt_hour(peak_hour)}[/bold]")
    console.print(f"  → Weekend warrior:    [bold]{weekend_pct:.1f}%[/bold] of commands on weekends")
    console.print(f"  → Early bird 🌅:      [bold]{early_bird_pct:.1f}%[/bold] before 9am")
    console.print(f"  → Night owl 🦉:       [bold]{night_owl_pct:.1f}%[/bold] after 10pm")
    console.print()

    # WORKSPACE
    if most_worked_dir:
        console.print(section("📁", "WORKSPACE", "magenta"))
        console.print(f"  → Most worked directory:")
        console.print(f"    [bold cyan]{most_worked_dir[0]}[/bold cyan]  [dim]({most_worked_dir[1]:,} commands)[/dim]")
        console.print()

    # SUCCESS RATE (shell-track only)
    if has_exit_codes:
        success = sum(1 for e in entries if e["exit_code"] == 0)
        failed = total - success
        success_pct = success / total * 100
        failed_counter = Counter(
            e["cmd"].split()[0] for e in entries
            if e["exit_code"] != 0 and e["cmd"].strip()
        )
        console.print(section("✅", "SUCCESS RATE", "green"))
        console.print(f"  → [bold]{success_pct:.1f}%[/bold] of commands succeeded")
        console.print(f"  → [green]✓ {success:,} succeeded[/green]   [red]✗ {failed:,} failed[/red]")
        if failed_counter:
            console.print(f"  → Most frustrating commands:")
            for cmd, cnt in failed_counter.most_common(3):
                console.print(f"    [red]{cmd}[/red]  [dim]({cnt} failures)[/dim]")
        console.print()

    # DURATION STATS (shell-track only)
    if has_durations:
        durations = [(e["cmd"], e["duration_ms"]) for e in entries if e["duration_ms"] is not None]
        if durations:
            fastest = sum(1 for _, d in durations if d < 1000)
            marathons = sum(1 for _, d in durations if d > 300_000)
            longest_cmd_str, longest_ms = max(durations, key=lambda x: x[1])
            longest_min = longest_ms // 60000
            longest_preview = longest_cmd_str[:50] + "..." if len(longest_cmd_str) > 50 else longest_cmd_str

            console.print(section("⏱️ ", "DURATION STATS", "yellow"))
            console.print(f"  → Speed demon:    [bold]{fastest:,}[/bold] commands under 1 second")
            console.print(f"  → Marathon runner:[bold]{marathons:,}[/bold] commands over 5 minutes")
            console.print(f"  → Longest: [bold]{longest_min}m[/bold]  [dim]{longest_preview}[/dim]")
            console.print()

    # FUN STATS
    console.print(section("🎮", "FUN STATS", "green"))
    console.print(f"  → Longest streak:    [bold]{longest_streak}[/bold] consecutive days 🔥")
    console.print(f"  → Command diversity: [bold]{unique_cmds:,}[/bold] unique commands")
    console.print(f"  → Longest command:   [bold]{len(longest_cmd_entry['cmd']):,}[/bold] characters")
    console.print(f"    [dim]{longest_cmd_preview}[/dim]")
    console.print()

    console.print(Panel(
        Text("shell-wrapped · your year in the terminal", justify="center", style="dim"),
        box=box.MINIMAL,
        border_style="dim",
    ))
    console.print()


if __name__ == "__main__":
    main()

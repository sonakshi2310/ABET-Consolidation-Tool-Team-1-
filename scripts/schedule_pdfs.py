"""Schedule PDF Fetcher - Set up automatic PDF fetching

QUICK START:
    # Show setup instructions
    python scripts/schedule_pdfs.py

    # Generate cron command
    python scripts/schedule_pdfs.py --cron

    # Generate systemd timer files
    python scripts/schedule_pdfs.py --systemd

USAGE:
    This script helps you set up automatic scheduling for fetch_pdfs.py.
    It generates the commands/files you need for cron, systemd, or Windows Task Scheduler.

SCHEDULING OPTIONS:
    1. Cron (Linux/Mac) - Recommended for simple scheduling
    2. Systemd Timer (Linux) - Recommended for Linux servers
    3. Windows Task Scheduler - For Windows servers
    4. GitHub Actions - For cloud-based scheduling

EXAMPLES:
    # Monthly on 1st at 9 AM (default)
    python scripts/schedule_pdfs.py --cron

    # Weekly on Mondays at 9 AM
    python scripts/schedule_pdfs.py --cron --weekly

    # Daily at 9 AM
    python scripts/schedule_pdfs.py --cron --daily

    # Custom schedule
    python scripts/schedule_pdfs.py --cron --time "14:30" --day 1  # 1st of month at 2:30 PM
"""
import os
import sys
import argparse
from pathlib import Path


def get_project_path():
    """Get the absolute path to the project root."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def get_python_path():
    """Get the Python executable path."""
    return sys.executable


def generate_cron_command(time: str = "09:00", day: int = None, weekly: bool = False, daily: bool = False):
    """Generate cron command.
    
    Args:
        time: Time in HH:MM format (24-hour)
        day: Day of month (1-31) for monthly, or day of week (0-7, 0=Sunday) for weekly
        weekly: If True, schedule weekly
        daily: If True, schedule daily
    """
    project_path = get_project_path()
    python_path = get_python_path()
    script_path = os.path.join(project_path, 'scripts', 'fetch_pdfs.py')
    
    hour, minute = time.split(':')
    
    if daily:
        # Daily: minute hour * * *
        cron_expr = f"{minute} {hour} * * *"
        description = "daily"
    elif weekly:
        # Weekly: minute hour * * day
        day_of_week = day if day is not None else 1  # Default to Monday
        cron_expr = f"{minute} {hour} * * {day_of_week}"
        description = f"weekly on day {day_of_week}"
    else:
        # Monthly: minute hour day * *
        day_of_month = day if day is not None else 1  # Default to 1st
        cron_expr = f"{minute} {hour} {day_of_month} * *"
        description = f"monthly on day {day_of_month}"
    
    command = f'cd {project_path} && {python_path} {script_path} >> logs/cron.log 2>&1'
    
    return cron_expr, command, description


def generate_systemd_files(time: str = "09:00", day: int = None, weekly: bool = False, daily: bool = False):
    """Generate systemd service and timer files."""
    project_path = get_project_path()
    python_path = get_python_path()
    script_path = os.path.join(project_path, 'scripts', 'fetch_pdfs.py')
    
    # Service file
    service_content = f"""[Unit]
Description=ABET PDF Fetcher
After=network.target

[Service]
Type=oneshot
User={os.getenv('USER', 'your-user')}
WorkingDirectory={project_path}
ExecStart={python_path} {script_path}
StandardOutput=journal
StandardError=journal
"""
    
    # Timer file
    if daily:
        on_calendar = f"*-*-* {time}:00"
        description = "daily"
    elif weekly:
        day_name = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][day if day is not None else 1]
        on_calendar = f"{day_name} {time}:00"
        description = f"weekly on {day_name}"
    else:
        day_of_month = day if day is not None else 1
        on_calendar = f"*-*-{day_of_month:02d} {time}:00"
        description = f"monthly on day {day_of_month}"
    
    timer_content = f"""[Unit]
Description=ABET PDF Fetcher Timer
Requires=abet-pdf-fetcher.service

[Timer]
OnCalendar={on_calendar}

[Install]
WantedBy=timers.target
"""
    
    return service_content, timer_content, description


def print_setup_instructions():
    """Print setup instructions for all scheduling methods."""
    project_path = get_project_path()
    python_path = get_python_path()
    
    print("=" * 70)
    print("PDF FETCHER SCHEDULING SETUP")
    print("=" * 70)
    print()
    
    print("OPTION 1: Cron (Linux/Mac) - Simplest")
    print("-" * 70)
    print("1. Edit crontab:")
    print("   crontab -e")
    print()
    print("2. Add one of these lines:")
    print()
    print("   # Monthly on 1st at 9 AM:")
    cron_expr, command, _ = generate_cron_command()
    print(f"   {cron_expr} {command}")
    print()
    print("   # Weekly on Mondays at 9 AM:")
    cron_expr, command, _ = generate_cron_command(weekly=True)
    print(f"   {cron_expr} {command}")
    print()
    print("   # Daily at 9 AM:")
    cron_expr, command, _ = generate_cron_command(daily=True)
    print(f"   {cron_expr} {command}")
    print()
    
    print("OPTION 2: Systemd Timer (Linux)")
    print("-" * 70)
    print("1. Run this script with --systemd to generate files")
    print("2. Copy service file to /etc/systemd/system/abet-pdf-fetcher.service")
    print("3. Copy timer file to /etc/systemd/system/abet-pdf-fetcher.timer")
    print("4. Enable and start:")
    print("   sudo systemctl enable abet-pdf-fetcher.timer")
    print("   sudo systemctl start abet-pdf-fetcher.timer")
    print()
    
    print("OPTION 3: Windows Task Scheduler")
    print("-" * 70)
    print("1. Open Task Scheduler")
    print("2. Create Basic Task")
    print("3. Set trigger (e.g., monthly on 1st at 9 AM)")
    print("4. Set action:")
    print(f"   Program: {python_path}")
    print(f"   Arguments: {os.path.join(project_path, 'scripts', 'fetch_pdfs.py')}")
    print(f"   Start in: {project_path}")
    print()
    
    print("OPTION 4: Test Manually")
    print("-" * 70)
    print(f"python {os.path.join(project_path, 'scripts', 'fetch_pdfs.py')}")
    print()
    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Set up automatic scheduling for PDF fetcher',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--cron', action='store_true', help='Generate cron command')
    parser.add_argument('--systemd', action='store_true', help='Generate systemd files')
    parser.add_argument('--time', default='09:00', help='Time in HH:MM format (default: 09:00)')
    parser.add_argument('--day', type=int, help='Day of month (1-31) or day of week (0-7)')
    parser.add_argument('--weekly', action='store_true', help='Schedule weekly instead of monthly')
    parser.add_argument('--daily', action='store_true', help='Schedule daily')
    args = parser.parse_args()
    
    if args.cron:
        cron_expr, command, description = generate_cron_command(
            args.time, args.day, args.weekly, args.daily
        )
        print(f"Cron expression ({description} at {args.time}):")
        print(f"  {cron_expr} {command}")
        print()
        print("Add this to your crontab (crontab -e):")
        print(f"  {cron_expr} {command}")
        
    elif args.systemd:
        service_content, timer_content, description = generate_systemd_files(
            args.time, args.day, args.weekly, args.daily
        )
        print(f"Systemd files ({description} at {args.time}):")
        print()
        print("Service file (save as /etc/systemd/system/abet-pdf-fetcher.service):")
        print("-" * 70)
        print(service_content)
        print()
        print("Timer file (save as /etc/systemd/system/abet-pdf-fetcher.timer):")
        print("-" * 70)
        print(timer_content)
        print()
        print("Then run:")
        print("  sudo systemctl enable abet-pdf-fetcher.timer")
        print("  sudo systemctl start abet-pdf-fetcher.timer")
        
    else:
        # Show all options
        print_setup_instructions()


if __name__ == '__main__':
    main()


"""Schedule PDF fetcher with cron

Usage:
    python scripts/schedule_pdfs.py --add --time "19:00"    # Add cron job (7 PM daily)
    python scripts/schedule_pdfs.py --add --time "09:00" --monthly  # Monthly at 9 AM
    python scripts/schedule_pdfs.py --remove                # Remove cron job
    python scripts/schedule_pdfs.py --show                  # Show current cron
"""
import os
import sys
import argparse
import subprocess
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(PROJECT_PATH, 'scripts', 'fetch_pdfs.py')
PYTHON_PATH = sys.executable
CRON_COMMENT = "# ABET PDF Fetcher"


def get_cron_entry(time: str, monthly: bool = False, weekly: bool = False, day: int = None):
    hour, minute = time.split(':')
    if monthly:
        day_str = str(day) if day else "1"
        cron_expr = f"{minute} {hour} {day_str} * *"
    elif weekly:
        day_str = str(day) if day else "1"  # Monday
        cron_expr = f"{minute} {hour} * * {day_str}"
    else:
        cron_expr = f"{minute} {hour} * * *"  # Daily
    command = f'cd {PROJECT_PATH} && {PYTHON_PATH} {SCRIPT_PATH} >> {PROJECT_PATH}/logs/cron.log 2>&1'
    return f"{cron_expr} {command} {CRON_COMMENT}"


def add_cron(time: str, monthly: bool, weekly: bool, day: int):
    entry = get_cron_entry(time, monthly, weekly, day)
    
    # Get current crontab
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        crontab = result.stdout
    except:
        crontab = ""
    
    # Remove old entry if exists
    lines = [l for l in crontab.split('\n') if CRON_COMMENT not in l and l.strip()]
    
    # Add new entry
    lines.append(entry)
    new_crontab = '\n'.join(lines) + '\n'
    
    # Install new crontab
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(new_crontab)
        temp_path = f.name
    
    try:
        subprocess.run(['crontab', temp_path], check=True)
        print(f"✓ Cron job added: {entry}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error adding cron: {e}")
        return False
    finally:
        os.unlink(temp_path)


def remove_cron():
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        crontab = result.stdout
    except:
        print("No crontab found")
        return False
    
    lines = [l for l in crontab.split('\n') if CRON_COMMENT not in l and l.strip()]
    new_crontab = '\n'.join(lines) + '\n' if lines else ''
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(new_crontab)
        temp_path = f.name
    
    try:
        subprocess.run(['crontab', temp_path], check=True)
        print("✓ Cron job removed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error removing cron: {e}")
        return False
    finally:
        os.unlink(temp_path)


def show_cron():
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        crontab = result.stdout
        if CRON_COMMENT in crontab:
            for line in crontab.split('\n'):
                if CRON_COMMENT in line:
                    print(line)
        else:
            print("No cron job found")
    except:
        print("No crontab found")


def main():
    parser = argparse.ArgumentParser(description='Schedule PDF fetcher')
    parser.add_argument('--add', action='store_true', help='Add cron job')
    parser.add_argument('--remove', action='store_true', help='Remove cron job')
    parser.add_argument('--show', action='store_true', help='Show current cron')
    parser.add_argument('--time', default='09:00', help='Time (HH:MM, default: 09:00)')
    parser.add_argument('--monthly', action='store_true', help='Run monthly')
    parser.add_argument('--weekly', action='store_true', help='Run weekly')
    parser.add_argument('--day', type=int, help='Day of month/week (1-31 or 0-7)')
    args = parser.parse_args()
    
    if args.add:
        add_cron(args.time, args.monthly, args.weekly, args.day)
    elif args.remove:
        remove_cron()
    elif args.show:
        show_cron()
    else:
        print("Use --add to add, --remove to remove, or --show to view cron job")
        print(f"Example: python scripts/schedule_pdfs.py --add --time 19:00")


if __name__ == '__main__':
    main()

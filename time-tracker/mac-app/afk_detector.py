#!/usr/bin/env python3
"""
AFK Detection using macOS IOKit.
Reads HIDIdleTime to determine user idle duration.
"""

import subprocess
import re


def get_idle_time() -> float:
    """
    Get system idle time in seconds.
    Uses ioreg to read HIDIdleTime from IOKit.

    Returns:
        float: Idle time in seconds, or 0.0 on error
    """
    try:
        # Run ioreg command to get idle time
        result = subprocess.run(
            ['ioreg', '-c', 'IOHIDSystem', '-d', '4'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return 0.0

        # Parse output for HIDIdleTime
        # Format: "HIDIdleTime" = 1234567890
        for line in result.stdout.split('\n'):
            if 'HIDIdleTime' in line:
                # Extract the number (nanoseconds)
                match = re.search(r'=\s*(\d+)', line)
                if match:
                    ns = int(match.group(1))
                    return ns / 1_000_000_000  # Convert to seconds

        return 0.0

    except subprocess.TimeoutExpired:
        return 0.0
    except Exception as e:
        print(f"Error getting idle time: {e}")
        return 0.0


def is_user_active(threshold_seconds: float = 30.0) -> bool:
    """
    Check if user is currently active (not idle).

    Args:
        threshold_seconds: Consider user active if idle less than this

    Returns:
        bool: True if user is active
    """
    return get_idle_time() < threshold_seconds


def format_duration(seconds: float) -> str:
    """Format duration as human-readable string."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        mins = int(seconds / 60)
        return f"{mins}m"
    else:
        hours = int(seconds / 3600)
        mins = int((seconds % 3600) / 60)
        return f"{hours}h {mins}m"


if __name__ == '__main__':
    # Test the detector
    import time

    print("AFK Detector Test")
    print("Move your mouse/keyboard to see idle time reset")
    print("-" * 40)

    while True:
        idle = get_idle_time()
        active = is_user_active()
        status = "ACTIVE" if active else "IDLE"
        print(f"\rIdle: {format_duration(idle):>8} | Status: {status}", end='', flush=True)
        time.sleep(1)

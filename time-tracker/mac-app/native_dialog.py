#!/usr/bin/env python3
"""
Native macOS dialogs for Time Tracker.
Uses PyObjC (included with macOS) to create proper multi-line text input dialogs.
"""

import subprocess
import sys


def show_activity_dialog(title="What are you doing?", subtitle="Log your current activity", default_text=""):
    """
    Show a native macOS dialog with a multi-line text input.
    Returns the entered text, or None if cancelled.
    """
    # Use AppleScript for a native multi-line dialog
    # This creates a dialog with a larger text area
    script = f'''
    tell application "System Events"
        activate
        set dialogResult to display dialog "{subtitle}" with title "{title}" default answer "{default_text}" buttons {{"Cancel", "Log"}} default button "Log" with icon note giving up after 300
        if gave up of dialogResult then
            return ""
        end if
        return text returned of dialogResult
    end tell
    '''

    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=310
        )

        if result.returncode == 0:
            text = result.stdout.strip()
            return text if text else None
        else:
            # User cancelled or error
            return None
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        print(f"Dialog error: {e}")
        return None


def show_activity_dialog_cocoa(title="What are you doing?", subtitle="Log your current activity", default_text=""):
    """
    Show a native macOS dialog using Cocoa/PyObjC with a proper multi-line text view.
    Returns the entered text, or None if cancelled.
    """
    try:
        from AppKit import (
            NSAlert, NSAlertFirstButtonReturn, NSApp, NSApplication,
            NSTextView, NSScrollView, NSBezelBorder, NSFont,
            NSMakeRect, NSViewWidthSizable, NSViewHeightSizable,
            NSModalResponseOK
        )
        from Foundation import NSObject

        # Ensure NSApplication is initialized
        if NSApp() is None:
            NSApplication.sharedApplication()

        # Create alert
        alert = NSAlert.alloc().init()
        alert.setMessageText_(title)
        alert.setInformativeText_(subtitle)
        alert.addButtonWithTitle_("Log")
        alert.addButtonWithTitle_("Cancel")
        alert.setAlertStyle_(0)  # NSAlertStyleWarning = 0, gives nice icon

        # Create scroll view with text view for multi-line input
        scroll_view = NSScrollView.alloc().initWithFrame_(NSMakeRect(0, 0, 350, 120))
        scroll_view.setBorderType_(NSBezelBorder)
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setHasHorizontalScroller_(False)
        scroll_view.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)

        # Create text view
        content_size = scroll_view.contentSize()
        text_view = NSTextView.alloc().initWithFrame_(
            NSMakeRect(0, 0, content_size.width, content_size.height)
        )
        text_view.setMinSize_(NSMakeRect(0, 0, content_size.width, content_size.height).size)
        text_view.setMaxSize_(NSMakeRect(0, 0, 10000, 10000).size)
        text_view.setVerticallyResizable_(True)
        text_view.setHorizontallyResizable_(False)
        text_view.setAutoresizingMask_(NSViewWidthSizable)
        text_view.textContainer().setWidthTracksTextView_(True)
        text_view.setFont_(NSFont.systemFontOfSize_(14))

        if default_text:
            text_view.setString_(default_text)

        scroll_view.setDocumentView_(text_view)
        alert.setAccessoryView_(scroll_view)

        # Make the text view first responder
        alert.window().setInitialFirstResponder_(text_view)

        # Run the alert
        response = alert.runModal()

        if response == NSAlertFirstButtonReturn:
            text = text_view.string()
            return text.strip() if text else None
        else:
            return None

    except ImportError as e:
        print(f"PyObjC not available: {e}")
        # Fall back to simple AppleScript dialog
        return show_activity_dialog(title, subtitle, default_text)
    except Exception as e:
        print(f"Cocoa dialog error: {e}")
        return show_activity_dialog(title, subtitle, default_text)


def show_afk_return_dialog(duration_str):
    """Show dialog when returning from AFK."""
    return show_activity_dialog_cocoa(
        title="Welcome back!",
        subtitle=f"You were away for {duration_str}. What were you doing?",
        default_text=""
    )


if __name__ == '__main__':
    # Test the dialog
    print("Testing native dialog...")
    result = show_activity_dialog_cocoa(
        title="What are you doing?",
        subtitle="Describe your current activity",
        default_text=""
    )
    if result:
        print(f"User entered: {result}")
    else:
        print("User cancelled")

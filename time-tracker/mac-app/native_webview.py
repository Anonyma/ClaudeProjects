#!/usr/bin/env python3
"""
Native WebKit window for the styled quick-log UI.
Falls back gracefully if WebKit isn't available.
"""

from pathlib import Path
from urllib.parse import urlencode, urlparse, urlunparse

_OPEN_WINDOWS = []


def _build_file_url(path: Path, params: dict) -> str:
    base = path.resolve().as_uri()
    if not params:
        return base
    parsed = urlparse(base)
    query = urlencode({k: v for k, v in params.items() if v is not None})
    return urlunparse(parsed._replace(query=query))


def show_quick_log_window(ping_id: str = None, on_logged=None) -> bool:
    """Open a native WebKit window for logging activity."""
    try:
        from AppKit import (
            NSApp,
            NSApplication,
            NSWindow,
            NSWindowStyleMaskTitled,
            NSWindowStyleMaskClosable,
            NSWindowStyleMaskResizable,
            NSBackingStoreBuffered,
            NSMakeRect,
            NSViewWidthSizable,
            NSViewHeightSizable,
        )
        from Foundation import NSObject, NSURL
        from WebKit import WKWebView, WKWebViewConfiguration, WKUserContentController
    except Exception as e:
        print(f"Native webview unavailable: {e}")
        return False

    if NSApp() is None:
        NSApplication.sharedApplication()

    html_path = Path(__file__).parent / "quick-log.html"
    if not html_path.exists():
        print(f"Quick log HTML not found: {html_path}")
        return False

    params = {}
    if ping_id:
        params["ping"] = ping_id

    url_str = _build_file_url(html_path, params)
    url = NSURL.URLWithString_(url_str)
    read_access = NSURL.fileURLWithPath_(str(html_path.parent))

    class QuickLogWindowController(NSObject):
        def initWithURL_onLogged_(self, load_url, on_logged_callback):
            self = super().init()
            if self is None:
                return None
            self.on_logged_callback = on_logged_callback

            style = (
                NSWindowStyleMaskTitled
                | NSWindowStyleMaskClosable
                | NSWindowStyleMaskResizable
            )
            frame = NSMakeRect(0, 0, 560, 640)
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                frame, style, NSBackingStoreBuffered, False
            )
            self.window.setTitle_("Time Tracker")
            self.window.setDelegate_(self)

            content_controller = WKUserContentController.alloc().init()
            content_controller.addScriptMessageHandler_name_(self, "close")
            content_controller.addScriptMessageHandler_name_(self, "logged")

            config = WKWebViewConfiguration.alloc().init()
            config.setUserContentController_(content_controller)

            self.webview = WKWebView.alloc().initWithFrame_configuration_(
                self.window.contentView().bounds(), config
            )
            self.webview.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
            self.window.setContentView_(self.webview)

            self.webview.loadFileURL_allowingReadAccessToURL_(load_url, read_access)
            self.window.center()
            self.window.makeKeyAndOrderFront_(None)
            NSApp().activateIgnoringOtherApps_(True)
            return self

        def userContentController_didReceiveScriptMessage_(self, _controller, message):
            try:
                name = message.name()
            except Exception:
                name = message.name
            try:
                body = message.body()
            except Exception:
                body = message.body

            if name == "logged" and self.on_logged_callback:
                try:
                    self.on_logged_callback(body)
                except Exception as e:
                    print(f"Log callback error: {e}")

            if name in ("logged", "close"):
                self.window.performClose_(None)

        def windowWillClose_(self, _notification):
            if self in _OPEN_WINDOWS:
                _OPEN_WINDOWS.remove(self)

    controller = QuickLogWindowController.alloc().initWithURL_onLogged_(url, on_logged)
    if controller is None:
        return False

    _OPEN_WINDOWS.append(controller)
    return True

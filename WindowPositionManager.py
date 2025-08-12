# encoding: utf-8
# WindowPositionManager.py
# MenuTitle: 還原工具視窗位置

from __future__ import division, print_function, unicode_literals
from AppKit import NSEvent, NSEventModifierFlagOption, NSApp, NSPoint, NSSize, NSRect, NSRunLoop, NSDate
from GlyphsApp import Glyphs
import time

__doc__="""
這個腳本可以記住和還原所有工具視窗的位置和大小。
預設行為：還原工具視窗位置（如果沒有記錄則先記錄）
按住 Option 鍵執行：記錄新位置
"""
# Configuration
PREFS_KEY = "com.YinTzuYuan.WindowPositionManager.positions"
WINDOW_TIMEOUT = 3.0
DEBUG_MODE = False  # Set to True to see detailed search process

def main():
    """Main execution function"""
    try:
        # Clear console for better readability
        Glyphs.clearLog()
        log_info("🎯 Window Position Manager")
        log_info("=" * 40)

        # Check if Option key is pressed
        option_pressed = is_option_key_pressed()

        if option_pressed:
            handle_save_positions()
        else:
            handle_restore_positions()

    except Exception as e:
        handle_error("Script execution failed", e)

def is_option_key_pressed():
    """Check if Option key is currently pressed"""
    modifier_flags = NSEvent.modifierFlags()
    return bool(modifier_flags & NSEventModifierFlagOption)

def handle_clear_config():
    """Handle clearing saved configuration"""
    log_info("🗑️ Clearing saved window positions...")

    config = load_config_from_prefs()
    if not config:
        show_result("No saved positions to clear", success=False)
        return

    try:
        del Glyphs.defaults[PREFS_KEY]
        window_count = len(config)
        show_result(f"Cleared {window_count} saved window positions", success=True)
        log_info("💡 Next execution will save current window positions")
    except Exception as e:
        handle_error("Failed to clear configuration", e)

def handle_save_positions():
    """Handle saving window positions"""
    start_time = time.time()
    log_info("🔄 Saving window positions...")

    tool_windows = get_tool_windows()
    if not tool_windows:
        show_result("No tool windows found to save", success=False)
        return

    window_configs = {}
    saved_count = 0

    for window in tool_windows:
        try:
            config = create_window_config(window)
            if config:
                window_configs[window.title()] = config
                saved_count += 1
                log_debug(f"Saved: {window.title()}")
        except Exception as e:
            log_error(f"Failed to save window: {window.title()}", e)

    execution_time = time.time() - start_time

    if saved_count > 0:
        save_config_to_prefs(window_configs)
        show_result(f"Saved {saved_count} window positions in {execution_time:.1f}s", success=True)
    else:
        show_result("No windows could be saved", success=False)

def handle_restore_positions():
    """Handle restoring window positions"""
    config = load_config_from_prefs()

    if not config:
        log_info("📝 No saved positions found. Saving current positions...")
        handle_save_positions()
        return

    start_time = time.time()
    log_info("🔄 Restoring window positions...")
    restored_count = restore_window_positions(config)
    execution_time = time.time() - start_time

    if restored_count > 0:
        show_result(f"Restored {restored_count} window positions in {execution_time:.1f}s", success=True)
    else:
        show_result("No windows could be restored (they might be inactive plugins)", success=False)
        log_info("💡 To restore plugin windows:")
        log_info("   1. Open the plugins manually first")
        log_info("   2. Then run this script again")

def get_tool_windows():
    """Get all visible tool windows (excluding main font editing windows)"""
    all_windows = NSApp.windows()
    tool_windows = []

    for window in all_windows:
        if not window.isVisible():
            continue

        if is_main_editing_window(window):
            continue

        tool_windows.append(window)
        log_debug(f"Found tool window: {window.title()}")

    return tool_windows

def is_main_editing_window(window):
    """Check if window is a main font editing window"""
    window_title = window.title()
    window_class = window.className()

    # Check file extension patterns in window title
    file_extensions = [".glyphs", ".ufo"]
    for ext in file_extensions:
        if ext in window_title:
            return True

    # Check window class patterns
    main_window_classes = ["GSDocument"]
    for class_pattern in main_window_classes:
        if class_pattern in window_class:
            return True

    # Check against open documents
    for doc in Glyphs.documents:
        if (doc.windowController() and
            doc.windowController().window() == window):
            return True

    return False

def create_window_config(window):
    """Create configuration dictionary for a window"""
    try:
        frame = window.frame()
        config = {
            'title': window.title(),
            'class': window.className(),
            'frame': {
                'x': float(frame.origin.x),
                'y': float(frame.origin.y),
                'width': float(frame.size.width),
                'height': float(frame.size.height)
            },
            'timestamp': time.time()
        }

        # Add delegate class info if available
        if hasattr(window, 'delegate') and window.delegate():
            delegate = window.delegate()
            if hasattr(delegate, 'className'):
                config['delegate_class'] = delegate.className()

        return config

    except Exception as e:
        log_error(f"Failed to create config for {window.title()}", e)
        return None

def restore_window_positions(config):
    """Restore window positions from configuration"""
    restored_count = 0
    skipped_count = 0
    total_count = len(config)

    log_info(f"🔄 Processing {total_count} windows...")

    for window_title, window_config in config.items():
        try:
            window = find_or_open_window(window_title, window_config)
            if window:
                if apply_window_frame(window, window_config['frame']):
                    restored_count += 1
                    log_debug(f"Restored: {window_title}")
                else:
                    log_error(f"Failed to apply frame to: {window_title}")
                    skipped_count += 1
            else:
                log_debug(f"Skipped (could not open): {window_title}")
                skipped_count += 1

        except Exception as e:
            log_error(f"Failed to restore {window_title}", e)
            skipped_count += 1

    # Show concise results
    if restored_count > 0:
        log_info(f"✅ Success: {restored_count}/{total_count} windows restored")
        if skipped_count > 0:
            log_info(f"ℹ️  Note: {skipped_count} windows skipped (may be inactive plugins)")
    else:
        log_info(f"ℹ️  No windows restored. {skipped_count} windows skipped.")

    return restored_count

def find_or_open_window(window_title, window_config):
    """Find existing window or try to open it"""
    # First, check if window is already open
    existing_window = find_window_by_title(window_title)
    if existing_window:
        log_debug(f"Found existing window: {window_title}")
        return existing_window

    log_debug(f"Attempting to open window: {window_title}")

    # Try to open the window
    opened_window = open_window_by_config(window_title, window_config)
    if opened_window:
        log_debug(f"Successfully opened: {window_title}")
        # Give window time to fully initialize
        time.sleep(0.5)
        return opened_window

    # If we can't open it, it might be a plugin that's not active
    # or a window that requires specific conditions
    log_debug(f"Could not open window: {window_title} (might be inactive plugin)")
    return None

def find_window_by_title(window_title):
    """Find window by title among all open windows"""
    all_windows = NSApp.windows()
    for window in all_windows:
        if window.isVisible() and window.title() == window_title:
            return window
    return None

def open_window_by_config(window_title, window_config):
    """Try to open window based on its configuration (improved version)"""
    delegate_class = window_config.get('delegate_class', '')

    # Handle specific window types first
    if open_specific_window_type(window_title, delegate_class):
        return wait_for_window(window_title)

    # Try comprehensive menu search
    if search_all_menus_for_window(window_title):
        return wait_for_window(window_title)

    return None

def open_specific_window_type(window_title, delegate_class):
    """Open specific types of windows using known methods"""
    try:
        # Macro Window
        if window_title in ['Macro Window', '巨集視窗'] or 'GSMacroViewController' in delegate_class:
            Glyphs.showMacroWindow()
            return True

        # Preview Window
        if window_title in ['Preview', '預覽']:
            if hasattr(Glyphs, 'showPreviewWindow'):
                Glyphs.showPreviewWindow()
                return True

        return False
    except Exception as e:
        log_error(f"Failed to open specific window type: {window_title}", e)
        return False

def search_all_menus_for_window(window_title):
    """Search through menus efficiently (priority order)"""
    log_debug(f"Searching menus for: {window_title}")

    # Priority menu order - most likely locations first
    priority_menus = [
        "腳本", "Script",      # Script menu (most plugins)
        "視窗", "Window",      # Window menu
        "檢視", "View",        # View menu
        "濾鏡", "Filter",      # Filter menu
    ]

    # Secondary menus
    other_menus = [
        "檔案", "File",
        "編輯", "Edit",
        "路徑", "Path",
        "協助", "Help"
    ]

    main_menu = NSApp.mainMenu()
    if not main_menu:
        return False

    # Search priority menus first
    for menu_title in priority_menus:
        menu = find_menu_by_title(menu_title, main_menu)
        if menu and search_menu_for_item(menu, window_title):
            return True

    # If not found, search other menus
    for menu_title in other_menus:
        menu = find_menu_by_title(menu_title, main_menu)
        if menu and search_menu_for_item(menu, window_title):
            return True

    return False

def find_menu_by_title(title, main_menu):
    """Find menu by title in main menu bar"""
    for i in range(main_menu.numberOfItems()):
        item = main_menu.itemAtIndex_(i)
        if item.title() == title:
            return item.submenu()
    return None

def search_menu_for_item(menu, target_title):
    """Search menu and submenus for target item (recursive)"""
    if not menu:
        return False

    try:
        for i in range(menu.numberOfItems()):
            item = menu.itemAtIndex_(i)
            item_title = item.title()

            # Skip empty items and separators
            if not item_title:
                continue

            # Check for match (exact, contains, or contained)
            if (target_title == item_title or
                target_title.lower() in item_title.lower() or
                item_title.lower() in target_title.lower()):

                log_debug(f"Found match: '{item_title}'")

                # Try to click the item
                if item.isEnabled():
                    menu.performActionForItemAtIndex_(i)
                    return True

            # Search submenu if exists
            if item.hasSubmenu():
                submenu = item.submenu()
                if search_menu_for_item(submenu, target_title):
                    return True

        return False

    except Exception as e:
        log_error(f"Error searching menu for {target_title}", e)
        return False

def try_open_preview():
    """Try to open preview window"""
    if hasattr(Glyphs, 'showPreviewWindow'):
        Glyphs.showPreviewWindow()
    else:
        # Fallback: try via menu
        try_click_menu_item("Window", "Preview")

def try_comprehensive_menu_search(window_title):
    """Comprehensive search through all menus and submenus"""
    log_debug(f"Searching menus for: {window_title}")

    try:
        main_menu = NSApp.mainMenu()
        if search_menu_recursively(main_menu, window_title):
            return wait_for_window(window_title)
    except Exception as e:
        log_error(f"Menu search failed for {window_title}", e)

    return None

def search_menu_recursively(menu, target_title):
    """Recursively search through menu and all submenus"""
    if not menu:
        return False

    try:
        for i in range(menu.numberOfItems()):
            item = menu.itemAtIndex_(i)
            item_title = item.title()

            # Skip separators and empty items
            if not item_title or item_title == "":
                continue

            # Check for exact match or partial match
            if (target_title == item_title or
                target_title.lower() in item_title.lower() or
                item_title.lower() in target_title.lower()):

                log_debug(f"Found menu match: '{item_title}' for '{target_title}'")
                if item.isEnabled():
                    menu.performActionForItemAtIndex_(i)
                    return True

            # Search in submenu if it exists
            if item.hasSubmenu():
                submenu = item.submenu()
                if search_menu_recursively(submenu, target_title):
                    return True

        return False

    except Exception as e:
        log_error(f"Error searching menu", e)
        return False

def try_click_menu_item(menu_name, item_name):
    """Try to click a menu item"""
    try:
        main_menu = NSApp.mainMenu()
        for i in range(main_menu.numberOfItems()):
            menu_item = main_menu.itemAtIndex_(i)
            if menu_item.title() == menu_name:
                submenu = menu_item.submenu()
                if submenu:
                    return find_and_click_menu_item(submenu, item_name)
        return False
    except:
        return False

def find_and_click_menu_item(menu, target_item):
    """Find and click menu item by name"""
    try:
        for i in range(menu.numberOfItems()):
            item = menu.itemAtIndex_(i)
            if target_item.lower() in item.title().lower():
                menu.performActionForItemAtIndex_(i)
                return True
        return False
    except:
        return False

def wait_for_window(window_title):
    """Wait for window to appear (improved with NSRunLoop like original)"""
    start_time = time.time()

    while time.time() - start_time < WINDOW_TIMEOUT:
        # Check if window exists
        window = find_window_by_title(window_title)
        if window:
            log_debug(f"Window appeared: {window_title}")
            return window

        # Use NSRunLoop for better responsiveness (like original version)
        NSRunLoop.currentRunLoop().runUntilDate_(
            NSDate.dateWithTimeIntervalSinceNow_(0.1)
        )

    log_debug(f"Timeout waiting for window: {window_title}")
    return None

def apply_window_frame(window, frame_config):
    """Apply frame configuration to window"""
    try:
        frame = NSRect(
            NSPoint(frame_config['x'], frame_config['y']),
            NSSize(frame_config['width'], frame_config['height'])
        )
        window.setFrame_display_(frame, True)
        return True
    except Exception as e:
        log_error(f"Failed to apply frame", e)
        return False

def save_config_to_prefs(config):
    """Save configuration to Glyphs preferences"""
    try:
        Glyphs.defaults[PREFS_KEY] = config
        log_debug(f"Saved configuration with {len(config)} windows")
    except Exception as e:
        log_error("Failed to save configuration", e)

def load_config_from_prefs():
    """Load configuration from Glyphs preferences"""
    try:
        config = Glyphs.defaults.get(PREFS_KEY)
        if config:
            log_debug(f"Loaded configuration with {len(config)} windows")
        return config
    except Exception as e:
        log_error("Failed to load configuration", e)
        return None

def show_result(message, success=True):
    """Show result to user via console and notification"""
    icon = "✅" if success else "⚠️"
    print(f"{icon} {message}")
    Glyphs.showNotification("Window Position Manager", message)

def handle_error(message, error=None):
    """Handle and display errors"""
    error_text = f"❌ {message}"
    if error:
        error_text += f": {error}"

    print(error_text)
    if DEBUG_MODE and error:
        import traceback
        traceback.print_exc()

    Glyphs.showNotification("Window Position Manager", f"Error: {message}")

def log_info(message):
    """Log informational message"""
    print(message)

def log_debug(message):
    """Log debug message (only if debug mode is enabled)"""
    if DEBUG_MODE:
        print(f"🔍 {message}")

def log_error(message, error=None):
    """Log error message"""
    error_text = f"❌ {message}"
    if error:
        error_text += f": {error}"
    print(error_text)

# Script execution
if __name__ == "__main__":
    main()
else:
    # Ensure script runs when called from menu
    main()

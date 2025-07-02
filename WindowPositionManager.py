# encoding: utf-8
# WindowPositionManager.py
#MenuTitle: 還原工具視窗位置
from __future__ import print_function, division, unicode_literals

from Foundation import NSPoint, NSSize, NSRect
from AppKit import NSApp, NSRunLoop, NSDate, NSEvent, NSEventModifierFlagOption
from GlyphsApp import Glyphs

import time
import traceback

__doc__="""
這個腳本可以記住和還原所有工具視窗的位置和大小。
預設行為：還原工具視窗位置（如果沒有記錄則先記錄）
按住 Option 鍵執行：記錄新位置
"""

# 全局變數
WINDOWS_CONFIG_KEY = "com.YinTzuYuan.windowsPositions"  # 用於儲存視窗配置的鍵
WINDOW_OPEN_TIMEOUT = 5.0  # 等待視窗開啟的最大秒數

class WindowPositionManager:
    def __init__(self):
        # 檢測 Option 鍵是否被按下
        keysPressed = NSEvent.modifierFlags()
        self.optionKeyPressed = keysPressed & NSEventModifierFlagOption == NSEventModifierFlagOption
        
        # 檢查是否有已保存的視窗配置
        self.window_configs = Glyphs.defaults.get(WINDOWS_CONFIG_KEY)
        
        # 根據按鍵狀態執行不同動作
        self.execute_action()
    
    def execute_action(self):
        """根據按鍵狀態執行相應動作"""
        try:
            if self.optionKeyPressed:
                # Option 鍵被按下：記錄新位置
                count = self.save_window_positions()
                if count > 0:
                    print(f"✅ 已記錄 {count} 個視窗位置")
                    Glyphs.showNotification("視窗位置管理器", f"已記錄 {count} 個視窗位置")
                else:
                    print("⚠️ 未找到可記錄的視窗")
                    Glyphs.showNotification("視窗位置管理器", "未找到可記錄的視窗")
            else:
                # 預設行為：還原位置，如果沒有記錄則先記錄
                if self.window_configs:
                    # 有記錄，執行還原
                    count = self.restore_window_positions()
                    if count > 0:
                        print(f"✅ 已還原 {count} 個視窗位置")
                        Glyphs.showNotification("視窗位置管理器", f"已還原 {count} 個視窗位置")
                    else:
                        print("⚠️ 無法還原視窗位置")
                        Glyphs.showNotification("視窗位置管理器", "無法還原視窗位置")
                else:
                    # 沒有記錄，先記錄當前位置
                    count = self.save_window_positions()
                    if count > 0:
                        print(f"📝 首次使用，已記錄 {count} 個視窗位置")
                        print("💡 提示：下次執行將還原這些位置，按住 Option 鍵執行可記錄新位置")
                        Glyphs.showNotification("視窗位置管理器", f"首次使用，已記錄 {count} 個視窗位置")
                    else:
                        print("⚠️ 未找到可記錄的視窗")
                        Glyphs.showNotification("視窗位置管理器", "未找到可記錄的視窗")
                        
        except Exception as e:
            error_msg = f"執行動作時發生錯誤：{str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            Glyphs.showNotification("視窗位置管理器", "執行時發生錯誤")
    
    # === 以下是原始的視窗管理邏輯 ===
    
    def find_menu_by_title(self, title):
        """查找特定標題的選單"""
        main_menu = NSApp.mainMenu()
        for i in range(main_menu.numberOfItems()):
            item = main_menu.itemAtIndex_(i)
            if item.title() == title:
                return item.submenu()
        return None
    
    def find_and_click_menu_item_by_title(self, menu, item_title):
        """在選單中查找並點擊項目"""
        if not menu:
            return False

        for i in range(menu.numberOfItems()):
            item = menu.itemAtIndex_(i)
            title = item.title()

            if item_title.lower() in title.lower():
                menu.performActionForItemAtIndex_(i)
                return True

            # 如果有子選單，也檢查它
            if item.hasSubmenu():
                submenu = item.submenu()
                if self.find_and_click_menu_item_by_title(submenu, item_title):
                    return True

        return False
    
    def search_menu_items_by_title(self, title):
        """在所有選單中搜尋項目"""
        # 常見選單標題 - 適用於不同語言版本
        common_menu_titles = ["File", "Edit", "View", "Path", "Filter", "Script", "Window", "Help",
                              "檔案", "編輯", "檢視", "路徑", "濾鏡", "腳本", "視窗", "協助"]

        for menu_title in common_menu_titles:
            menu = self.find_menu_by_title(menu_title)
            if menu and self.find_and_click_menu_item_by_title(menu, title):
                return True

        return False
    
    def get_tool_windows(self):
        """獲取所有非主視窗的工具視窗"""
        all_windows = NSApp.windows()
        tool_windows = []

        # 找出所有工具視窗
        for window in all_windows:
            # 過濾條件：
            # 1. 窗口必須可見
            # 2. 不是主編輯器窗口
            if window.isVisible():
                is_main_window = False

                # 檢查視窗標題（現在不需要檢查本腳本視窗，因為沒有 UI）
                window_title = window.title()

                # 檢查是否為主窗口
                # 方法 1: 檢查窗口類名
                window_class = window.className()
                if "GSDocument" in window_class:
                    is_main_window = True

                # 方法 2: 檢查窗口代理類名
                if hasattr(window, "delegate") and window.delegate():
                    delegate = window.delegate()
                    if hasattr(delegate, "className"):
                        delegate_class = delegate.className()
                        if any(x in delegate_class for x in ["GSFontViewController", "GSDocumentWindowController", "GSEditViewController"]):
                            is_main_window = True

                # 方法 3: 檢查是否在 Glyphs.documents 列表中的窗口
                for doc in Glyphs.documents:
                    if doc.windowController() and doc.windowController().window() == window:
                        is_main_window = True
                        break

                # 方法 4: 檢查窗口標題是否包含常見的字體編輯器標題特徵
                if window_title.endswith(".glyphs") or window_title.endswith(".ufo"):
                    is_main_window = True

                # 如果不是主窗口，添加到工具窗口列表
                if not is_main_window:
                    tool_windows.append(window)

        return tool_windows
    
    def save_window_positions(self):
        """保存視窗位置和尺寸"""
        try:
            tool_windows = self.get_tool_windows()
            window_configs = {}

            for window in tool_windows:
                window_title = window.title()
                frame = window.frame()
                window_class = window.className()

                # 建立視窗配置
                window_config = {
                    "title": window_title,
                    "class": window_class,
                    "x": frame.origin.x,
                    "y": frame.origin.y,
                    "width": frame.size.width,
                    "height": frame.size.height
                }

                # 識別特定視窗類型
                if hasattr(window, "delegate") and window.delegate():
                    delegate = window.delegate()
                    if hasattr(delegate, "className"):
                        delegate_class = delegate.className()
                        window_config["delegate_class"] = delegate_class

                # 保存視窗
                window_configs[window_title] = window_config

            # 保存到 Glyphs 的預設設定中
            Glyphs.defaults[WINDOWS_CONFIG_KEY] = window_configs
            return len(window_configs)

        except Exception as e:
            print("儲存視窗位置時發生錯誤：", e)
            traceback.print_exc()
            return 0
    
    def wait_for_window_to_appear(self, window_title, timeout=WINDOW_OPEN_TIMEOUT):
        """等待視窗出現"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            all_windows = NSApp.windows()
            for window in all_windows:
                if window.isVisible() and window.title() == window_title:
                    return window

            # 短暫等待，讓界面有響應時間
            NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.1))

        return None
    
    def open_macro_window(self):
        """開啟巨集視窗"""
        Glyphs.showMacroWindow()
        return self.wait_for_window_to_appear("Macro Window")
    
    def open_specific_window(self, config):
        """嘗試開啟特定類型的視窗"""
        window_title = config["title"]
        delegate_class = config.get("delegate_class", "")

        # 檢查視窗是否已存在
        all_windows = NSApp.windows()
        for window in all_windows:
            if window.isVisible() and window.title() == window_title:
                return window

        # 巨集視窗 (Macro Window)
        if window_title == "Macro Window" or delegate_class == "GSMacroViewController":
            return self.open_macro_window()

        # 預覽視窗
        elif window_title == "Preview" or delegate_class == "PreviewTextWindow":
            try:
                # 嘗試使用 Glyphs 的預覽功能
                if hasattr(Glyphs, 'showPreviewWindow'):
                    Glyphs.showPreviewWindow()
                else:
                    # 如果沒有直接方法，嘗試透過選單開啟
                    window_menu = self.find_menu_by_title("Window")
                    if window_menu:
                        self.find_and_click_menu_item_by_title(window_menu, "Preview")
            except:
                pass
            return self.wait_for_window_to_appear("Preview")

        # 視窗選單中的項目
        window_menu = self.find_menu_by_title("Window")
        if not window_menu:
            window_menu = self.find_menu_by_title("視窗")

        if window_menu and self.find_and_click_menu_item_by_title(window_menu, window_title):
            return self.wait_for_window_to_appear(window_title)

        # 常見視窗對應的選單位置
        common_window_locations = {
            "Font Info": ("Font", "Font Info"),
            "Layers": ("View", "Show Layers"),
            "Palette": ("View", "Show Palette"),
            "Properties": ("View", "Show Properties"),
            "Transformations": ("View", "Show Transformations"),
            "Kerning": ("Window", "Kerning"),
            "Metrics": ("Window", "Metrics"),
            "Notes": ("Window", "Notes"),
            "Glyphs": ("Window", "Glyphs"),
            "Plugin Manager": ("Window", "Plugin Manager"),
            "Glyph Info": ("Window", "Glyph Info"),
            "Filters": ("Window", "Filters"),
        }

        # 檢查常見位置
        for key, (menu_name, item_name) in common_window_locations.items():
            if key in window_title:
                menu = self.find_menu_by_title(menu_name)
                if menu and self.find_and_click_menu_item_by_title(menu, item_name):
                    return self.wait_for_window_to_appear(window_title)

        # 在所有選單中搜尋
        if self.search_menu_items_by_title(window_title):
            return self.wait_for_window_to_appear(window_title)

        return None
    
    def restore_window_positions(self):
        """恢復視窗位置和尺寸"""
        try:
            window_configs = Glyphs.defaults[WINDOWS_CONFIG_KEY]
            if not window_configs:
                return 0

            restored_count = 0

            # 遍歷每個儲存的視窗配置
            for window_title, config in window_configs.items():
                # 檢查視窗是否已經開啟
                all_windows = NSApp.windows()
                existing_window = None

                for window in all_windows:
                    if window.isVisible() and window.title() == window_title:
                        existing_window = window
                        break

                # 如果視窗未開啟，嘗試開啟它
                if not existing_window:
                    existing_window = self.open_specific_window(config)

                    # 給視窗一些時間完全初始化
                    if existing_window:
                        time.sleep(0.3)

                # 如果視窗現在可用，設定其位置和尺寸
                if existing_window:
                    frame = NSRect(
                        NSPoint(config["x"], config["y"]),
                        NSSize(config["width"], config["height"])
                    )
                    existing_window.setFrame_display_(frame, True)
                    restored_count += 1

            return restored_count

        except Exception as e:
            print("還原視窗位置時發生錯誤：", e)
            traceback.print_exc()
            return 0

# 主程式執行
def main():
    """主函數 - 清理日誌並執行視窗位置管理器"""
    try:
        # 清理巨集視窗日誌
        Glyphs.clearLog()
        print("🎯 視窗位置管理器")
        print("=" * 30)
        
        # 建立並執行管理器
        manager = WindowPositionManager()
        
    except Exception as e:
        print(f"❌ 啟動視窗位置管理器時發生錯誤：{e}")
        import traceback
        traceback.print_exc()
        # 顯示巨集視窗以便查看錯誤
        Glyphs.showMacroWindow()

# 執行主函數
if __name__ == "__main__":
    main()
else:
    main()

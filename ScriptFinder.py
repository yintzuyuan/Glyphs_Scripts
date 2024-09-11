# MenuTitle: 腳本搜尋器...
# -*- coding: utf-8 -*-
__doc__="""
搜尋並執行 Glyphs 腳本的工具。
可以搜尋腳本名稱、作者和描述，並直接執行選中的腳本。
"""

import vanilla
import os
import re
from GlyphsApp import *
from GlyphsApp.plugins import *
import os
from Foundation import NSURL
from AppKit import NSWorkspace
import traceback

class ScriptFinderTool:
    def __init__(self):
        self.debug_mode = False  # 調試模式開關
        # 取得腳本資訊
        self.scripts_info = self.get_scripts_info()

        # 設定初始大小和最小大小
        initial_width = 600
        initial_height = 400
        min_width = 400
        min_height = 300

        # 建立 GUI
        self.w = vanilla.Window((initial_width, initial_height), "腳本搜尋器", minSize=(min_width, min_height))

        # 搜尋欄
        self.w.searchBox = vanilla.SearchBox((10, 10, -60, 20), placeholder="搜尋腳本...", callback=self.search_scripts)

        # 左側腳本列表（寬度會自動調整）
        self.w.scriptList = vanilla.List((10, 40, -210, -10), [], selectionCallback=self.show_script_details)

        # 右側詳細資訊（固定寬度）
        self.w.detailsBox = vanilla.TextEditor((-200, 40, -10, -40), "", readOnly=True)

        # 執行按鈕
        self.w.runButton = vanilla.Button((-200, -30, -10, 20), "執行腳本", callback=self.run_script)
        self.w.runButton.enable(False)  # 初始時停用按鈕

        # 添加重新整理按鈕
        self.w.reloadButton = vanilla.Button((-50, 10, -10, 20), "↺", callback=self.reload_scripts)

        # 設定字體
        self.w.detailsBox.getNSTextView().setFont_(NSFont.systemFontOfSize_(12))

        # 初始化列表
        self.update_script_list(self.scripts_info)

        self.w.open()

    def get_scripts_info(self):
        """取得腳本資訊"""
        directory_path = os.path.expanduser('~/Library/Application Support/Glyphs 3/Scripts')
        scripts_info = self.read_py_files_in_directory(directory_path)

        # 從結果中移除工具自身的腳本
        scripts_info = [script for script in scripts_info if script['script_name'] != "腳本搜尋器..."]

        return scripts_info

    def read_py_files_in_directory(self, directory):
        """讀取目錄中的 Python 檔案"""
        py_files_info = []
        skip_folders = ['fontTools', 'robofab', 'vanilla']

        self.debug_print(f"開始讀取目錄: {directory}")

        try:
            items = os.listdir(directory)
            author_folders = []
            for item in items:
                item_path = os.path.join(directory, item)
                self.debug_print(f"處理項目: {item_path}")
                resolved_path = self.get_original_path(item_path)
                self.debug_print(f"解析後的路徑: {resolved_path}")
                if os.path.isdir(resolved_path) and item not in skip_folders:
                    author_folders.append((item, resolved_path))
                    self.debug_print(f"添加作者資料夾: {item} -> {resolved_path}")
                else:
                    self.debug_print(f"跳過項目: {item}")
        except Exception as e:
            print(f"讀取目錄 {directory} 時發生錯誤: {str(e)}")
            return py_files_info

        self.debug_print(f"找到的作者資料夾: {[af[0] for af in author_folders]}")

        for author_folder, author_path in author_folders:
            self.debug_print(f"處理作者資料夾: {author_folder} (路徑: {author_path})")

            if not os.path.exists(author_path):
                print(f"警告：資料夾不存在 {author_path}")
                continue

            for root, dirs, files in os.walk(author_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        self.debug_print(f"處理檔案: {file_path}")
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                script_info = self.extract_script_info(file_path, content, author_folder)
                                if script_info:
                                    script_info["file_path"] = file_path
                                    py_files_info.append(script_info)
                                    self.debug_print(f"成功提取腳本資訊: {script_info['script_name']}")
                                else:
                                    self.debug_print(f"無法提取腳本資訊: {file_path}")
                        except Exception as e:
                            print(f"讀取檔案 {file_path} 時發生錯誤: {str(e)}")

        print(f"總共提取了 {len(py_files_info)} 個腳本資訊資訊")
        return py_files_info

    def get_original_path(self, path, max_depth=5):
        """
        遞迴解析替身檔案的原始路徑
        max_depth: 最大遞迴深度，防止無限循環
        """
        if max_depth <= 0:
            return path

        try:
            # 檢查是否為符號連結
            if os.path.islink(path):
                resolved_path = os.path.realpath(path)
                if resolved_path != path:
                    return self.get_original_path(resolved_path, max_depth - 1)

            # 使用 NSURL 解析 Finder 別名
            url = NSURL.fileURLWithPath_(path)
            if url.isFileReferenceURL():
                resolved_url = url.fileReferenceURL().filePathURL()
                if resolved_url:
                    resolved_path = resolved_url.path()
                    if os.path.exists(resolved_path) and resolved_path != path:
                        return self.get_original_path(resolved_path, max_depth - 1)

            # 如果無法解析或不是替身，返回原始路徑
            return path

        except Exception as e:
            print(f"解析替身檔案時發生錯誤 {path}: {str(e)}")
            return path

    def extract_script_info(self, file_path, file_content, author_folder):
        """從腳本內容中提取資訊"""
        author = author_folder

        menu_title_match = re.search(r'^#\s*MenuTitle:\s*(.+)$', file_content, re.MULTILINE)
        if menu_title_match:
            script_name = menu_title_match.group(1).strip()
        else:
            # 如果沒有 MenuTitle，則不顯示在清單中
            return None

        doc_match = re.search(r'__doc__\s*=\s*"""([\s\S]*?)"""', file_content)
        description = doc_match.group(1).strip() if doc_match else "無說明"

        # 檢查是否使用了 vanilla 模組
        def check_vanilla_usage(file_content):
            import_pattern = r'^(?!#).*import\s+vanilla'
            from_import_pattern = r'^(?!#).*from\s+vanilla\s+import'

            uses_vanilla = (
                re.search(import_pattern, file_content, re.MULTILINE) is not None or
                re.search(from_import_pattern, file_content, re.MULTILINE) is not None
            )

            return uses_vanilla

        uses_vanilla = check_vanilla_usage(file_content)

        # 如果使用了 vanilla,在說明前加上 (GUI) 標記
        if uses_vanilla:
            description = "(GUI) " + description

        return {
            "author": author,
            "script_name": script_name,
            "description": description,
            "file_path": file_path  # 添加文件路徑到返回的字典中
        }

    def search_scripts(self, sender):
        """搜尋腳本"""
        query = sender.get().lower()
        filtered_scripts = [
            script for script in self.scripts_info
            if query in script['script_name'].lower() or
            query in script['author'].lower() or
            query in script['description'].lower()
        ]
        self.update_script_list(filtered_scripts)

    def update_script_list(self, scripts):
        """更新腳本列表"""
        self.current_scripts = scripts
        script_names = [script['script_name'] for script in scripts]

        self.w.scriptList.set(script_names)

        # 如果腳本列表為空，清空詳細資訊並禁用執行按鈕
        if not scripts:
            self.w.detailsBox.set("")
            self.w.runButton.enable(False)
            self.selected_script_path = None

    def show_script_details(self, sender):
        """顯示腳本詳細資訊"""
        selection = sender.getSelection()
        if selection and self.current_scripts:
            script = self.current_scripts[selection[0]]

            # 從描述中分離 GUI 標記和實際描述
            description = script['description']
            gui_tag = ""
            if description.startswith("(GUI) "):
                gui_tag = "(GUI)"
                description = description[6:].strip()  # 移除 "(GUI) " 前綴

            details = "{} {}\n\n作者：{}\n\n說明：\n{}".format(
                script['script_name'], gui_tag, script['author'], description)
            self.w.detailsBox.set(details)

            # 啟用執行按鈕並儲存選中腳本的路徑
            self.w.runButton.enable(True)
            self.selected_script_path = script['file_path']
        else:
            # 如果沒有選擇或腳本列表為空，清空詳細資訊並禁用執行按鈕
            self.w.detailsBox.set("")
            self.w.runButton.enable(False)
            self.selected_script_path = None

    def reload_scripts(self, sender=None):
        """重新加載所有腳本"""
        print("開始重新加載腳本...")  # 這個資訊總是顯示
        self.scripts_info = self.get_scripts_info()
        self.update_script_list(self.scripts_info)
        print(f"重新加載完成,共加載 {len(self.scripts_info)} 個腳本")  # 這個資訊總是顯示

    def debug_print(self, *args, **kwargs):
        if self.debug_mode:
            print(*args, **kwargs)

    def toggle_debug_mode(self, sender):
        self.debug_mode = not self.debug_mode
        status = "開啟" if self.debug_mode else "關閉"
        print(f"調試模式已{status}")  # 這裡使用普通的 print,因為我們總是想看到這條消息

    def run_script(self, sender):
        """執行選中的腳本"""
        try:
            if hasattr(self, 'selected_script_path') and self.selected_script_path:
                # 獲取當前字體
                font = Glyphs.font
                if font is None:
                    print("請先打開一個字體文件")
                    return

                # 準備全局命名空間
                global_namespace = {
                    'Glyphs': Glyphs,
                    'font': font,
                    'selectedLayers': font.selectedLayers,
                    'selectedGlyphs': [layer.parent for layer in font.selectedLayers],
                    # 添加其他可能需要的全局變量
                }

                # 讀取腳本內容
                with open(self.selected_script_path, 'r', encoding='utf-8') as file:
                    script_content = file.read()

                # 執行腳本
                exec(script_content, global_namespace)
            else:
                print("請先選擇一個腳本")
        except NameError as e:
            print(f"執行腳本時發生名稱錯誤：{e}")
            print("這可能是因為腳本使用了未定義的變數或函數。")
            print("請檢查腳本是否與當前版本的 Glyphs 相容，或是否缺少必要的導入語句。")
        except Exception as e:
            print(f"執行腳本時發生錯誤：{e}")
            print("錯誤詳情：")
            traceback.print_exc()

ScriptFinderTool()

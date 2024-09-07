# MenuTitle: 腳本搜尋器
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
import traceback

class ScriptFinderTool:
    def __init__(self):
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
        self.w.searchBox = vanilla.SearchBox((10, 10, -10, 20), placeholder="搜尋腳本...", callback=self.search_scripts)

        # 左側腳本列表（寬度會自動調整）
        self.w.scriptList = vanilla.List((10, 40, -210, -40), [], selectionCallback=self.show_script_details)

        # 右側詳細資訊（固定寬度）
        self.w.detailsBox = vanilla.TextEditor((-200, 40, -10, -40), "", readOnly=True)

        # 執行按鈕
        self.w.runButton = vanilla.Button((10, -30, 180, 20), "執行腳本", callback=self.run_script)
        self.w.runButton.enable(False)  # 初始時停用按鈕

        # 設定字體
        self.w.detailsBox.getNSTextView().setFont_(NSFont.systemFontOfSize_(12))

        # 初始化列表
        self.update_script_list(self.scripts_info)

        self.w.open()

    def get_scripts_info(self):
        """取得腳本資訊"""
        directory_path = os.path.expanduser('~/Library/Application Support/Glyphs 3/Scripts')
        return self.read_py_files_in_directory(directory_path)

    def read_py_files_in_directory(self, directory):
        """讀取目錄中的 Python 檔案"""
        py_files_info = []
        skip_folders = ['fontTools', 'robofab', 'vanilla']

        author_folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f)) and f not in skip_folders]

        for author_folder in author_folders:
            author_path = os.path.join(directory, author_folder)

            if os.path.islink(author_path):
                resolved_path = self.get_original_path(author_path)
                if resolved_path:
                    author_path = resolved_path
                else:
                    print(traceback.format_exc())
                    continue

            for root, dirs, files in os.walk(author_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                script_info = self.extract_script_info(file_path, content, author_folder)
                                if script_info:
                                    script_info["file_path"] = file_path
                                    py_files_info.append(script_info)
                        except Exception as e:
                            print(traceback.format_exc())

        return py_files_info

    def get_original_path(self, alias_path):
        """解析替身檔案的原始路徑"""
        try:
            return os.readlink(alias_path)
        except OSError:
            try:
                from Foundation import NSURL
                from AppKit import NSWorkspace, NSURLBookmarkResolutionWithoutUI, NSURLBookmarkResolutionWithoutMounting
                workspace = NSWorkspace.sharedWorkspace()
                url = NSURL.fileURLWithPath_(alias_path)
                original_url = workspace.resolveForAliasFileAtURL_options_error_(url, NSURLBookmarkResolutionWithoutUI | NSURLBookmarkResolutionWithoutMounting, None)[0]
                if original_url:
                    return original_url.path()
            except Exception as e:
                print(f"解析替身檔案時發生錯誤：{str(e)}")

        print(f"無法解析替身檔案：{alias_path}")
        return None

    def extract_script_info(self, file_path, file_content, author_folder):
        """從腳本內容中提取資訊"""
        author = author_folder

        menu_title_match = re.search(r'^#\s*MenuTitle:\s*(.+)$', file_content, re.MULTILINE)
        if menu_title_match:
            script_name = menu_title_match.group(1).strip()
        else:
            return None

        doc_match = re.search(r'__doc__\s*=\s*"""([\s\S]*?)"""', file_content)
        description = doc_match.group(1).strip() if doc_match else "無說明"

        return {
            "author": author,
            "script_name": script_name,
            "description": description
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
        self.w.scriptList.set([script['script_name'] for script in scripts])
        
        # 如果腳本列表為空，清空詳細資訊並禁用執行按鈕
        if not scripts:
            self.w.detailsBox.set("")
            self.w.runButton.enable(False)
            self.selected_script_path = None

    def show_script_details(self, sender):
        """顯示腳本詳細資訊"""
        selection = sender.getSelection()
        if selection and self.current_scripts:  # 檢查是否有選擇和腳本列表是否為空
            script = self.current_scripts[selection[0]]
            details = f"{script['script_name']}\n\n作者：{script['author']}\n\n說明：\n{script['description']}"
            self.w.detailsBox.set(details)

            # 啟用執行按鈕並儲存選中腳本的路徑
            self.w.runButton.enable(True)
            self.selected_script_path = script['file_path']
        else:
            # 如果沒有選擇或腳本列表為空，清空詳細資訊並禁用執行按鈕
            self.w.detailsBox.set("")
            self.w.runButton.enable(False)
            self.selected_script_path = None

    def run_script(self, sender):
        """執行選中的腳本"""
        try:
            if hasattr(self, 'selected_script_path') and self.selected_script_path:
                exec(open(self.selected_script_path).read())
            else:
                print("請先選擇一個腳本")
        except Exception as e:
            print(f"執行程式碼時發生錯誤：{e}")

ScriptFinderTool()
# -*- coding: utf-8 -*-
# 用法: 進入 tools 目錄，執行 python README_updateList.py
# 描述: 這個工具會自動更新 README.md 的腳本列表，讓你不用手動維護。請確保你的README.md中包含## 腳本列表這個標題，腳本會在這個標題下方放置腳本列表。

import os

def get_script_descriptions(directory):
    descriptions = {"主目錄": []}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".py") and filename != "README_updateList.py":
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        start = content.find('"""')
                        end = content.find('"""', start + 3)
                        menu_title_start = content.find('# MenuTitle:')
                        menu_title_end = content.find('\n', menu_title_start) if menu_title_start != -1 else -1
                        
                        if start != -1 and end != -1:
                            description = content[start + 3:end].strip()
                            menu_title = content[menu_title_start + len('# MenuTitle:'):menu_title_end].strip() if menu_title_start != -1 else filename
                            relative_path = os.path.relpath(root, directory)
                            section_title = relative_path if relative_path != "." else "主目錄"
                            if section_title not in descriptions:
                                descriptions[section_title] = []
                            descriptions[section_title].append(f"- **{menu_title}** : {description}")
                except IOError as e:
                    print(f"Error reading file {file_path}: {e}")
    return descriptions

def update_readme(readme_path, descriptions):
    try:
        with open(readme_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        start_index = None
        end_index = None
        for i, line in enumerate(lines):
            if line.strip() == "## 腳本列表":
                start_index = i
            elif start_index is not None and line.strip().startswith("## "):
                end_index = i
                break

        if start_index is not None:
            if end_index is None:
                end_index = len(lines)
            
            new_lines = lines[:start_index + 1] + ["\n"]  # 標題後加空行
            
            # 先加入主目錄的內容
            if "主目錄" in descriptions:
                new_lines.extend([item + "\n" for item in sorted(descriptions["主目錄"])])
                new_lines.extend(["\n"])  # 主目錄內容後加兩個空行
            
            # 再加入子資料夾的內容
            for section, descs in sorted(descriptions.items()):
                if section != "主目錄":
                    new_lines.extend([f"### {section}\n"])  # 子資料夾標題後加空行
                    new_lines.extend([item + "\n" for item in sorted(descs)])
                    new_lines.append("\n")  # 每個子資料夾後加空行
            
            # new_lines.append("\n")  # 整個列表最後加空行
            new_lines += lines[end_index:]
            
            with open(readme_path, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
        else:
            print("Error: '## 腳本列表' section not found in README.md")
    except IOError as e:
        print(f"Error updating README file: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(script_dir, "..")  # 請確保這是正確的目錄路徑
    readme_path = os.path.join(script_dir, "../README.md")
    descriptions = get_script_descriptions(directory)
    update_readme(readme_path, descriptions)

# MenuTitle: 貼上 編碼→字符
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Glyphs 剪貼簿編碼轉換腳本
將剪貼簿中的 Glyphs 編碼格式（如 uni6771, U+6771 等）轉換為對應字符並貼到游標處

支援的編碼格式：
- uni6771 (Glyphs Unicode 格式)
- U+6771 (標準 Unicode 格式)
- 0x6771 (十六進位格式)
- 26481 (十進位格式)
- 6771 (純十六進位數字)

支援功能：
- 單一編碼轉換
- 多行編碼批量轉換
- 自動識別編碼格式
- 錯誤處理與詳細報告
"""

import re
import subprocess
from GlyphsApp import *

def get_clipboard_content():
    """取得剪貼簿內容"""
    try:
        # 使用 pbpaste 命令取得剪貼簿內容
        result = subprocess.run(['pbpaste'], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"無法取得剪貼簿內容: {e}")
        return None

def parse_encoding_format(text):
    """解析各種編碼格式並返回 Unicode 碼點"""
    if not text:
        return None
    
    text = text.strip()
    
    # 支援的格式模式
    patterns = [
        # uni6771 格式
        (r'^uni([0-9A-Fa-f]{4,6})$', 16),
        # U+6771 格式
        (r'^U\+([0-9A-Fa-f]{4,6})$', 16),
        # 0x6771 格式
        (r'^0x([0-9A-Fa-f]{4,6})$', 16),
        # 純十六進位 6771
        (r'^([0-9A-Fa-f]{4,6})$', 16),
        # 十進位格式 26481
        (r'^(\d{1,7})$', 10),
    ]
    
    for pattern, base in patterns:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            try:
                code_point = int(match.group(1), base)
                # 檢查是否為有效的 Unicode 範圍
                if 0 <= code_point <= 0x10FFFF:
                    return code_point
            except ValueError:
                continue
    
    return None

def parse_multiple_encodings(text):
    """解析多行編碼格式並返回 Unicode 碼點列表"""
    if not text:
        return []
    
    lines = text.strip().split('\n')
    code_points = []
    failed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:  # 跳過空行
            continue
            
        code_point = parse_encoding_format(line)
        if code_point is not None:
            code_points.append((line, code_point))
        else:
            failed_lines.append(line)
    
    return code_points, failed_lines

def unicode_to_character(code_point):
    """將 Unicode 碼點轉換為字符"""
    try:
        return chr(code_point)
    except ValueError:
        return None

def get_glyph_name_from_unicode(code_point):
    """從 Unicode 碼點取得 Glyph 名稱"""
    try:
        # 將 Unicode 碼點轉換為十六進位字串
        unicode_hex = f"{code_point:04X}"
        glyph_info = Glyphs.glyphInfoForUnicode(unicode_hex)
        if glyph_info and glyph_info.name:
            return glyph_info.name
        else:
            # 如果找不到對應的 glyph info，嘗試使用 uni + 十六進位格式
            return f"uni{unicode_hex}"
    except Exception as e:
        print(f"無法取得 Glyph 名稱: {e}")
        return None

def insert_at_cursor(text_to_insert):
    """在游標位置插入文字"""
    # 取得目前的字型和分頁
    font = Glyphs.font
    if not font:
        print("沒有開啟的字型檔案")
        return False
    
    # 取得目前的編輯視圖
    current_tab = font.currentTab
    if not current_tab:
        print("沒有開啟的編輯分頁")
        return False
    
    try:
        # 取得目前游標位置
        cursor_pos = current_tab.textCursor
        current_text = current_tab.text or ""
        
        # 在游標位置插入文字
        new_text = current_text[:cursor_pos] + text_to_insert + current_text[cursor_pos:]
        current_tab.text = new_text
        
        # 移動游標到插入文字的結尾
        current_tab.textCursor = cursor_pos + len(text_to_insert)
        
        return True
    except Exception as e:
        print(f"插入文字時發生錯誤: {e}")
        return False

def main():
    """主要執行函式"""
    # 取得剪貼簿內容
    clipboard_content = get_clipboard_content()
    
    if not clipboard_content:
        Message("剪貼簿是空的或無法讀取", "請複製要轉換的編碼到剪貼簿")
        return
    
    print(f"剪貼簿內容: {clipboard_content}")
    
    # 檢查是否為多行內容
    lines = clipboard_content.strip().split('\n')
    
    if len(lines) > 1:
        # 處理多行編碼
        code_points, failed_lines = parse_multiple_encodings(clipboard_content)
        
        if not code_points and failed_lines:
            Message("無法識別的編碼格式", 
                    f"剪貼簿中沒有可識別的編碼格式\n\n" +
                    "支援的格式：\n" +
                    "• uni6771\n" +
                    "• U+6771\n" +
                    "• 0x6771\n" +
                    "• 6771\n" +
                    "• 26481")
            return
        
        # 轉換所有有效的編碼為字符
        characters = []
        conversion_info = []
        
        for original_text, code_point in code_points:
            character = unicode_to_character(code_point)
            if character:
                characters.append(character)
                conversion_info.append(f"{original_text} → {character} (U+{code_point:04X})")
                print(f"{original_text} → {character} (U+{code_point:04X})")
        
        if not characters:
            Message("無法轉換為字符", "沒有可轉換的有效 Unicode 碼點")
            return
        
        # 將所有字符組合成字串
        result_text = ''.join(characters)
        
        # 插入到游標位置
        if insert_at_cursor(result_text):
            # 準備詳細的轉換資訊
            info_text = f"成功轉換 {len(characters)} 個編碼：\n\n"
            info_text += '\n'.join(conversion_info[:10])  # 最多顯示 10 個
            if len(conversion_info) > 10:
                info_text += f"\n... 還有 {len(conversion_info) - 10} 個"
            
            if failed_lines:
                info_text += f"\n\n無法識別 {len(failed_lines)} 個格式：\n"
                info_text += '\n'.join(failed_lines[:5])  # 最多顯示 5 個失敗的
                if len(failed_lines) > 5:
                    info_text += f"\n... 還有 {len(failed_lines) - 5} 個"
            
            # Message("批量轉換成功", info_text)
        else:
            Message("插入失敗", "無法將字符插入到編輯視圖")
            
    else:
        # 處理單行編碼（原有邏輯）
        code_point = parse_encoding_format(clipboard_content)
        
        if code_point is None:
            Message("無法識別的編碼格式", 
                    f"剪貼簿內容「{clipboard_content}」不是支援的編碼格式\n\n" +
                    "支援的格式：\n" +
                    "• uni6771\n" +
                    "• U+6771\n" +
                    "• 0x6771\n" +
                    "• 6771\n" +
                    "• 26481")
            return
        
        # 轉換為字符
        character = unicode_to_character(code_point)
        
        if not character:
            Message("無法轉換為字符", f"Unicode 碼點 {code_point} 無法轉換為有效字符")
            return
        
        print(f"Unicode 碼點: {code_point} (U+{code_point:04X})")
        print(f"對應字符: {character}")
        
        # 嘗試取得對應的 Glyph 名稱
        glyph_name = get_glyph_name_from_unicode(code_point)
        if glyph_name:
            print(f"Glyph 名稱: {glyph_name}")
        
        # 插入到游標位置
        if insert_at_cursor(character):
            # 顯示成功訊息
            pass
            # Message("轉換成功", 
            #         f"已將「{clipboard_content}」轉換為「{character}」並插入到游標位置\n\n" +
            #         f"Unicode: U+{code_point:04X}\n" +
            #         f"字符: {character}" +
            #         (f"\nGlyph: {glyph_name}" if glyph_name else ""))
        else:
            Message("插入失敗", "無法將字符插入到編輯視圖")

# 執行主函式
if __name__ == "__main__":
    main()
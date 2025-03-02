# MenuTitle: 新增筆劃屬性
# -*- coding: utf-8 -*-
__doc__ = """
向選取的路徑新增筆劃屬性。
如果沒有選取路徑，則處理目前字符的所有路徑。
可以同時處理多個選取字符和多個圖層。
"""

from GlyphsApp import *
from vanilla import *

class StrokeAttributesDialog:
    def __init__(self):
        # 定義預設值儲存的鍵
        self.keyPrefix = "com.YinTzuYuan.StrokeAttributes"
        self.strokeWidthKey = f"{self.keyPrefix}.strokeWidth"
        self.strokeHeightKey = f"{self.keyPrefix}.strokeHeight"

        # 從預設值讀取之前的設定
        savedStrokeWidth = Glyphs.defaults.get(self.strokeWidthKey) or "10"
        savedStrokeHeight = Glyphs.defaults.get(self.strokeHeightKey) or ""

        # 視窗大小設定
        self.w = FloatingWindow((220, 110), "新增筆劃屬性")

        # 建立輸入欄位
        self.w.strokeWidthText = TextBox((10, 12, 70, 20), "寬度:", sizeStyle="small")
        self.w.strokeWidth = EditText((80, 10, 130, 22), savedStrokeWidth, sizeStyle="small")

        self.w.strokeHeightText = TextBox((10, 40, 70, 20), "高度:", sizeStyle="small")
        self.w.strokeHeight = EditText((80, 38, 130, 22), savedStrokeHeight, placeholder="選填", sizeStyle="small")

        # 建立按鈕
        self.w.applyButton = Button((10, 70, 100, 25), "新增", callback=self.applyCallback)
        self.w.removeButton = Button((120, 70, 90, 25), "移除", callback=self.removeCallback)

        # 顯示視窗
        self.w.open()

    def applyCallback(self, sender):
        # 取得輸入值
        strokeWidth = self.w.strokeWidth.get().strip()
        strokeHeight = self.w.strokeHeight.get().strip()

        # 檢查筆劃寬度是否有值
        if not strokeWidth:
            print("請輸入筆劃寬度")
            return

        try:
            # 保存用戶輸入的設定
            Glyphs.defaults[self.strokeWidthKey] = strokeWidth
            Glyphs.defaults[self.strokeHeightKey] = strokeHeight

            strokeWidth = int(strokeWidth)
            strokeHeight = int(strokeHeight) if strokeHeight else None
            self.processLayers(True, strokeWidth, strokeHeight)
        except ValueError:
            print("請輸入有效的數字")

    def removeCallback(self, sender):
        self.processLayers(False)

    def processLayers(self, add=True, strokeWidth=None, strokeHeight=None):
        font = Glyphs.font
        if not font:
            print("沒有開啟的字型檔案")
            return

        # 取得選取的字符
        selectedLayers = font.selectedLayers
        if not selectedLayers:
            print("沒有選取字符")
            return

        processed_paths = 0
        processed_glyphs = 0

        # 如果處理多個字符，先禁用界面更新以提高效率
        if len(selectedLayers) > 1:
            font.disableUpdateInterface()

        try:
            for layer in selectedLayers:
                glyph = layer.parent

                if not glyph:
                    continue

                # 開始記錄變更
                glyph.beginUndo()

                # 處理所有圖層
                for l in glyph.layers:
                    # 如果是在編輯模式且只有一個圖層被選取，則檢查路徑選取狀態
                    # 否則，處理所有路徑(字符選取模式)
                    if len(selectedLayers) == 1 and layer == font.selectedLayers[0]:
                        selectedPaths = [p for p in l.paths if p.selected]
                        pathsToProcess = selectedPaths if selectedPaths else l.paths
                    else:
                        # 字符選取模式 - 處理所有路徑
                        pathsToProcess = l.paths

                    for path in pathsToProcess:
                        if add:
                            # 新增筆劃屬性
                            path.attributes['strokeWidth'] = strokeWidth
                            if strokeHeight is not None:
                                path.attributes['strokeHeight'] = strokeHeight
                        else:
                            # 關閉 fill 和 mask 屬性
                            path.attributes['fill'] = False
                            path.attributes['mask'] = False
                            # 移除筆劃屬性
                            if 'strokeWidth' in path.attributes:
                                del path.attributes['strokeWidth']
                            if 'strokeHeight' in path.attributes:
                                del path.attributes['strokeHeight']

                        processed_paths += 1

                # 結束記錄變更
                glyph.endUndo()
                processed_glyphs += 1

        finally:
            # 無論處理是否順利完成，都確保重新啟用界面更新
            if len(selectedLayers) > 1:
                font.enableUpdateInterface()

            # 強制重繪所有視圖
            Glyphs.redraw()

        if add:
            statusMessage = f"已新增筆劃屬性: 寬度={strokeWidth}"
            if strokeHeight is not None:
                statusMessage += f", 高度={strokeHeight}"
        else:
            statusMessage = "已移除筆劃屬性"

        print(f"{statusMessage}，處理了 {processed_glyphs} 個字符的 {processed_paths} 條路徑。")

# 執行腳本
StrokeAttributesDialog()

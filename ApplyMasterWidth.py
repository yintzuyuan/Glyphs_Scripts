# MenuTitle: 套用主板寬度到所有圖層
# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
__doc__ = """
讀取當前主板的圖層寬度，並將此寬度套用到當前主板中的所有圖層。
支援批次處理多個字符，每個字符使用自己的主板寬度。
"""

from GlyphsApp import *


def apply_master_width():
    """套用主板寬度到所有圖層"""
    font = Glyphs.font

    # 檢查前置條件
    if not font:
        print("錯誤：沒有開啟的字型檔案")
        return

    selectedLayers = font.selectedLayers
    if not selectedLayers:
        print("錯誤：沒有選取字符")
        return

    currentMaster = font.selectedFontMaster
    if not currentMaster:
        print("錯誤：無法取得當前主板")
        return

    masterId = currentMaster.id
    processed_glyphs = 0
    processed_layers = 0

    # 如果處理多個字符，先禁用界面更新以提高效率
    if len(selectedLayers) > 1:
        font.disableUpdateInterface()

    try:
        for selectedLayer in selectedLayers:
            glyph = selectedLayer.parent

            if not glyph:
                continue

            # 取得該字符主板圖層的寬度
            masterLayer = glyph.layers[masterId]
            if not masterLayer:
                print(f"警告：字符 '{glyph.name}' 沒有主板圖層")
                continue

            masterWidth = masterLayer.width

            # 開始記錄變更
            glyph.beginUndo()

            # 套用到該字符所有屬於當前主板的圖層
            for layer in glyph.layers:
                # 跳過不屬於當前主板的圖層
                if layer.associatedMasterId != masterId:
                    continue

                # 套用寬度
                layer.width = masterWidth
                processed_layers += 1

            # 結束記錄變更
            glyph.endUndo()
            processed_glyphs += 1

    finally:
        # 無論處理是否順利完成，都確保重新啟用界面更新
        if len(selectedLayers) > 1:
            font.enableUpdateInterface()

        # 強制重繪所有畫面
        Glyphs.redraw()

    print(f"完成：已處理 {processed_glyphs} 個字符的 {processed_layers} 個圖層")


# 執行腳本
apply_master_width()

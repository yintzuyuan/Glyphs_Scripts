# MenuTitle: 新增筆劃屬性...
# -*- coding: utf-8 -*-
__doc__ = """
向選取的路徑新增筆劃屬性。
如果沒有選取路徑，則處理目前字符的所有路徑。
可以同時處理多個選取字符和多個圖層。
此版本不使用Vanilla模組，改用原生Cocoa元素。
"""

from GlyphsApp import *
import objc
from Foundation import NSRect, NSMakeRect, NSObject, NSString, NSTextField, NSButton
from AppKit import NSWindow, NSApp, NSView, NSAlert, NSTextFieldCell, NSSmallControlSize
from AppKit import NSWindowStyleMaskTitled, NSWindowStyleMaskClosable

class StrokeAttributesDialogNative(NSObject):
    
    def init(self):
        self = objc.super(StrokeAttributesDialogNative, self).init()
        if self:
            # 定義預設值儲存的鍵
            self.keyPrefix = "com.YinTzuYuan.StrokeAttributes"
            self.strokeWidthKey = "%s.strokeWidth" % self.keyPrefix
            self.strokeHeightKey = "%s.strokeHeight" % self.keyPrefix
            
            # 從預設值讀取之前的設定
            savedStrokeWidth = Glyphs.defaults.get(self.strokeWidthKey) or "10"
            savedStrokeHeight = Glyphs.defaults.get(self.strokeHeightKey) or ""
            
            # 建立視窗
            windowWidth = 220
            windowHeight = 110
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                NSMakeRect(0, 0, windowWidth, windowHeight),
                NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
                2, False
            )
            self.window.setTitle_("新增筆劃屬性")
            
            # 建立主視圖
            self.contentView = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, windowWidth, windowHeight))
            self.window.setContentView_(self.contentView)
            
            # 建立寬度標籤
            widthLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(10, 80, 70, 20))
            widthLabel.setStringValue_("寬度:")
            widthLabel.setBezeled_(False)
            widthLabel.setDrawsBackground_(False)
            widthLabel.setEditable_(False)
            widthLabel.setSelectable_(False)
            self.contentView.addSubview_(widthLabel)
            
            # 建立寬度輸入欄位
            self.widthField = NSTextField.alloc().initWithFrame_(NSMakeRect(80, 80, 130, 22))
            self.widthField.setStringValue_(savedStrokeWidth)
            self.contentView.addSubview_(self.widthField)
            
            # 建立高度標籤
            heightLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(10, 50, 70, 20))
            heightLabel.setStringValue_("高度:")
            heightLabel.setBezeled_(False)
            heightLabel.setDrawsBackground_(False)
            heightLabel.setEditable_(False)
            heightLabel.setSelectable_(False)
            self.contentView.addSubview_(heightLabel)
            
            # 建立高度輸入欄位
            self.heightField = NSTextField.alloc().initWithFrame_(NSMakeRect(80, 50, 130, 22))
            self.heightField.setStringValue_(savedStrokeHeight)
            self.heightField.setPlaceholderString_("選填")
            self.contentView.addSubview_(self.heightField)
            
            # 建立新增按鈕
            self.applyButton = NSButton.alloc().initWithFrame_(NSMakeRect(10, 10, 100, 25))
            self.applyButton.setTitle_("新增")
            self.applyButton.setAction_(objc.selector(self.applyCallback_, signature=b"v@:@"))
            self.applyButton.setTarget_(self)
            self.contentView.addSubview_(self.applyButton)
            
            # 建立移除按鈕
            self.removeButton = NSButton.alloc().initWithFrame_(NSMakeRect(120, 10, 90, 25))
            self.removeButton.setTitle_("移除")
            self.removeButton.setAction_(objc.selector(self.removeCallback_, signature=b"v@:@"))
            self.removeButton.setTarget_(self)
            self.contentView.addSubview_(self.removeButton)
            
            # 顯示視窗
            self.window.center()
            self.window.makeKeyAndOrderFront_(None)
        return self
    
    def applyCallback_(self, sender):
        # 取得輸入值
        strokeWidth = self.widthField.stringValue().strip()
        strokeHeight = self.heightField.stringValue().strip()
        
        # 檢查筆劃寬度是否有值
        if not strokeWidth:
            self.showAlert_("請輸入筆劃寬度")
            return
        
        try:
            # 保存用戶輸入的設定
            Glyphs.defaults[self.strokeWidthKey] = strokeWidth
            Glyphs.defaults[self.strokeHeightKey] = strokeHeight
            
            strokeWidth = int(strokeWidth)
            strokeHeight = int(strokeHeight) if strokeHeight else None
            
            # 呼叫 Python 方法
            self.processLayers(True, strokeWidth, strokeHeight)
        except ValueError:
            self.showAlert_("請輸入有效的數字")
    
    def removeCallback_(self, sender):
        # 呼叫 Python 方法
        self.processLayers(False, None, None)
    
    def showAlert_(self, message):
        alert = NSAlert.alloc().init()
        alert.setMessageText_(message)
        alert.runModal()
    
    @objc.python_method
    def processLayers(self, add, strokeWidth, strokeHeight):
        """Python 方法處理圖層而不是直接使用 Objective-C 橋接"""
        font = Glyphs.font
        if not font:
            self.showAlert_("沒有開啟的字型檔案")
            return
        
        # 取得選取的字符
        selectedLayers = font.selectedLayers
        if not selectedLayers:
            self.showAlert_("沒有選取字符")
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
            
            # 強制重繪所有畫面
            Glyphs.redraw()
        
        if add:
            statusMessage = "已新增筆劃屬性: 寬度=%s" % strokeWidth
            if strokeHeight is not None:
                statusMessage += ", 高度=%s" % strokeHeight
        else:
            statusMessage = "已移除筆劃屬性"
        
        print("%s，處理了 %d 個字符的 %d 條路徑。" % (statusMessage, processed_glyphs, processed_paths))

# 執行腳本
dialog = StrokeAttributesDialogNative.alloc().init()
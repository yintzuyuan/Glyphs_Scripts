#MenuTitle: 新增智慧組件編輯框...
# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
__doc__="""
自動新增圖層和配對智慧組件長寬軸（可選擇是否新增最小圖層）
"""
import vanilla
from GlyphsApp import *

class SmartBBox(object):
    def __init__(self): # 視窗

        # self.clear_preferences() # 清除偏好設定(測試用)
        
        # 視窗 'self.w':
        # edY = 22 # 編輯框行高
        # txY  = 20 # 文字行高text
        # sp = 10 # 邊緣間隔space
        # l = 30 # 總行高
        # btnX = 120 # 按鈕寬度button
        # btnY = 20 # 按鈕高度
        windowWidth = 320
        windowHeight = 190


        self.w = vanilla.FloatingWindow(
            ( windowWidth, windowHeight ), # default window size
            "新增智慧組件編輯框", # 視窗標題
            autosaveName = "com.YinTzuYuan.SmartBBox.mainwindow" # stores last window position and size
        )

        # UI 元素:
        self.w.Text_layer = vanilla.TextBox('auto', "圖層名稱（窄－扁）")
        self.w.editText_1 = vanilla.EditText('auto', placeholder="圖層名稱")
        self.w.editText_2 = vanilla.EditText('auto', placeholder="圖層名稱")
        self.w.Text_value = vanilla.TextBox('auto', "數值範圍（小－大）")
        self.w.editText_3 = vanilla.EditText('auto', placeholder="數值")
        self.w.editText_4 = vanilla.EditText('auto', placeholder="數值")
        self.w.checkbox_5 = vanilla.CheckBox('auto', "加入最小圖層", value=False, callback=self.checkboxCallback)
        self.w.editText_5 = vanilla.EditText('auto', placeholder="圖層名稱", readOnly=False)
        # 按鈕:
        self.w.button = vanilla.Button('auto', "加入編輯框", callback=self.run_script_BBox) # 確定執行腳本

        rules = [
            # 水平對齊
            "H:|-sp-[Text_layer]-sp-|",
            "H:|-sp-[editText_1]-[editText_2(==editText_1)]-sp-|",
            "H:|-sp-[Text_value]-sp-|",
            "H:|-sp-[editText_3]-[editText_4(==editText_3)]-sp-|",
            "H:|-sp-[checkbox_5]-[editText_5]-sp-|",
            "H:|-sp-[button]-sp-|",
            # 垂直對齊
            "V:|-sp-[Text_layer]-sp-[editText_1]-sp-[Text_value]-sp-[editText_3]-sp-[checkbox_5]-sp-[button]-sp-|",
            "V:|-sp-[Text_layer]-sp-[editText_2]-sp-[Text_value]-sp-[editText_4]-sp-[editText_5]-sp-[button]-sp-|",
        ]
        metrics = {
            "sp" : 10,
        }

        # 開啟視窗並聚焦:
        self.w.addAutoPosSizeRules(rules, metrics)
        self.w.open()
        self.w.makeKey()
        self.w.setDefaultButton(self.w.button)

        if not self.LoadPreferences():
            print("無法載入用戶偏好設定，將重置為預設值。")
            self.DefaultPreferences()

    def checkboxCallback(self, sender):
        # 根據複選框的狀態啟用或禁用文字輸入欄位
        self.w.editText_5.enable(sender.get())
        # 將復選框的新狀態保存到用戶偏好設定
        Glyphs.defaults["com.YinTzuYuan.SmartBBox.checkbox_5"] = sender.get()

    def DefaultPreferences(self): # 預設值
        try:
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_5"] = "Minimize"
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_1"] = "Wilted"
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_2"] = "Flat"
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_3"] = "0"
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_4"] = "100"
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.checkbox_5"] = False
        except Exception as e:
            print(f"Error saving Default: {e}") # 錯誤回報
            return False
        return True

    def SavePreferences(self, sender): # 保存偏好設定
        try:
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_5"] = self.w.editText_5.get()
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_1"] = self.w.editText_1.get()
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_2"] = self.w.editText_2.get()
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_3"] = self.w.editText_3.get()
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_4"] = self.w.editText_4.get()
            Glyphs.defaults["com.YinTzuYuan.SmartBBox.checkbox_5"] = self.w.checkbox_5.get()
        except Exception as e:
            print(f"Error saving preferences: {e}") # 錯誤回報
            return False
        return True

    def LoadPreferences(self): # 載入偏好設定
        try:
            self.w.editText_5.set(Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_5"])
            self.w.editText_1.set(Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_1"])
            self.w.editText_2.set(Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_2"])
            self.w.editText_3.set(Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_3"])
            self.w.editText_4.set(Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_4"])
            self.w.checkbox_5.set(Glyphs.defaults["com.YinTzuYuan.SmartBBox.checkbox_5"])
        except Exception as e:
            # print(f"Error loading preferences: {e}") # 錯誤回報
            return False
        
        return True
    
    # def clear_preferences(self): # 清除偏好設定(測試用)
    #     del Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_5"]
    #     del Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_1"]
    #     del Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_2"]
    #     del Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_3"]
    #     del Glyphs.defaults["com.YinTzuYuan.SmartBBox.editText_4"]
    #     del Glyphs.defaults["com.YinTzuYuan.SmartBBox.checkbox_5"]


    def run_script_BBox(self, sender): # 執行腳本
        try:
            enable_custom_layer = self.w.checkbox_5.get()
            custom_layer_name = self.w.editText_5.get()
            miniWidth_layer_name = self.w.editText_1.get()
            miniHeight_layer_name = self.w.editText_2.get()

            # 嘗試從UI元件獲取並轉換數值
            try:
                miniNum_Value = float(self.w.editText_3.get())
                maxNum_Value = float(self.w.editText_4.get())
            except ValueError:
                # 如果轉換失敗，提醒用戶並終止腳本執行
                Message("輸入錯誤", "請確保在數值欄位中輸入有效的數字。")
                return

            # 新增圖層部分

            try:
                thisFont = Glyphs.font
                currentMaster = thisFont.selectedFontMaster

                for thisGlyph in [l.parent for l in thisFont.selectedLayers]:
                    # print("Processing %s" % thisGlyph.name)

                    # 檢查是否有窄圖層
                    all_layers = thisGlyph.layers
                    has_miniWidth_layer = False
                    for layer in all_layers:
                        if layer.name == miniWidth_layer_name:
                            has_miniWidth_layer = True
                            # print("已經存在" + miniWidth_layer_name + "圖層。")
                            break

                    # 若沒有就新增一個窄圖層
                    if not has_miniWidth_layer:
                        newLayer = GSLayer()
                        newLayer = thisGlyph.layers[currentMaster.id].copy()
                        newLayer.associatedMasterId = currentMaster.id
                        newLayer.name = miniWidth_layer_name
                        # print("新增圖層：%s" % newLayer.name)
                        thisGlyph.layers.append(newLayer)

                    # 檢查是否有扁圖層
                    has_miniHeight_layer = False
                    for layer in all_layers:
                        if layer.name == miniHeight_layer_name:
                            has_miniHeight_layer = True
                            # print("已經存在" + miniHeight_layer_name + "圖層。")
                            break

                    # 若沒有就新增一個扁圖層
                    if not has_miniHeight_layer:
                        newLayer = GSLayer()
                        newLayer = thisGlyph.layers[currentMaster.id].copy()
                        newLayer.associatedMasterId = currentMaster.id
                        newLayer.name = miniHeight_layer_name
                        # print("新增圖層：%s" % newLayer.name)
                        thisGlyph.layers.append(newLayer)

                    # 若啟用自訂圖層名稱，則新增自訂圖層
                    if enable_custom_layer:
                        has_custom_layer = False
                        for layer in all_layers:
                            if layer.name == custom_layer_name:
                                has_custom_layer = True
                                # print("已經存在" + custom_layer_name + "圖層。")
                                break

                        if not has_custom_layer:
                            newLayer = GSLayer()
                            newLayer = thisGlyph.layers[currentMaster.id].copy()
                            newLayer.associatedMasterId = currentMaster.id
                            newLayer.name = custom_layer_name
                            # print("新增圖層：%s" % newLayer.name)
                            thisGlyph.layers.append(newLayer)
            except Exception as e:
                    Glyphs.showMacroWindow()
                    print("SmartBBox Error (add_layer): %s" % e) # 錯誤回報

            # 增加智慧組件軸
                    
            def find_or_create_axis(glyph, axis_name, min_value, max_value):
                    smartComponentAxes = glyph.smartComponentAxes or []
                    
                    # 在已有的軸中查找是否存在同名軸
                    for axis in smartComponentAxes:
                        if axis.name == axis_name:
                            # 如果找到了同名軸，更新其值並返回
                            axis.topValue = max_value
                            axis.bottomValue = min_value
                            return axis
                        
                    # 如果未找到軸，則創建新軸
                    new_axis = GSSmartComponentAxis()
                    new_axis.name = axis_name
                    new_axis.topValue = max_value
                    new_axis.bottomValue = min_value
                    glyph.smartComponentAxes.append(new_axis)
                    return new_axis
            GSLayer.color
            
            for layer in thisFont.selectedLayers:
                glyph = layer.parent  
                # print(type(glyph))  # 應該顯示 <class 'GSGlyph'>
                # 確保 "Width" 和 "Height" 軸存在
                smartWidthAxis = find_or_create_axis(glyph, "Width", miniNum_Value, maxNum_Value)
                smartHeightAxis = find_or_create_axis(glyph, "Height", miniNum_Value, maxNum_Value)


            # 智慧組件配對圖層
            for layer in thisFont.selectedLayers:
                # 主要圖層
                layer.parent.layers[0].smartComponentPoleMapping[smartWidthAxis.id] = 2  # Regular 寬度值設定
                layer.parent.layers[0].smartComponentPoleMapping[smartHeightAxis.id] = 2  # Regular 長度值設定
                # 窄圖層
                layer.parent.layers[miniWidth_layer_name].smartComponentPoleMapping[smartWidthAxis.id] = 1  # 窄圖層 寬度值設定
                layer.parent.layers[miniWidth_layer_name].smartComponentPoleMapping[smartHeightAxis.id] = 2  # 窄圖層 長度值設定
                # 扁圖層
                layer.parent.layers[miniHeight_layer_name].smartComponentPoleMapping[smartWidthAxis.id] = 2  # 扁圖層 寬度值設定
                layer.parent.layers[miniHeight_layer_name].smartComponentPoleMapping[smartHeightAxis.id] = 1  # 扁圖層 長度值設定
                # 最小圖層
                if enable_custom_layer:
                    layer.parent.layers[custom_layer_name].smartComponentPoleMapping[smartWidthAxis.id] = 1
                    layer.parent.layers[custom_layer_name].smartComponentPoleMapping[smartHeightAxis.id] = 1

            if not self.SavePreferences(self):
                print("SmartBBox 無法寫入用戶偏好設定。")
            
        
        except Exception as e:
            Glyphs.showMacroWindow()
            print("SmartBBox Error (run_script_BBox): %s" % e) # 錯誤回報
        

SmartBBox()

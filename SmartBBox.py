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
		# 視窗 'self.w':
		edY = 22 # 編輯框行高
		txY  = 20 # 文字行高text
		sp = 10 # 邊緣間隔space
		l = 30 # 總行高
		btnX = 120 # 按鈕寬度button
		btnY = 20 # 按鈕高度
		windowWidth = 320
		windowHeight = 190


		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"新增智慧組件編輯框", # 視窗標題
			autosaveName = "com.YinTzuYuan.SmartBBox.mainwindow" # stores last window position and size
		)

		# UI 元素:
		self.w.Text_layer = vanilla.TextBox((sp, sp, -sp, txY), "圖層名稱（窄－扁）")
		self.w.editText_1 = vanilla.EditText((sp, sp+l, 150, edY), placeholder="圖層名稱")
		self.w.editText_2 = vanilla.EditText((170, sp+l, -sp, edY), placeholder="圖層名稱")
		self.w.Text_value = vanilla.TextBox((sp, sp+l*2, -sp, txY), "數值範圍（小－大）")
		self.w.editText_3 = vanilla.EditText((sp, sp+l*3, 150, edY), placeholder="數值")
		self.w.editText_4 = vanilla.EditText((170, sp+l*3, -sp, edY), placeholder="數值")
		self.w.checkbox_5 = vanilla.CheckBox((sp, sp+l*4, 150, txY), "加入最小圖層", value=False, callback=self.checkboxCallback)
		self.w.editText_5 = vanilla.EditText((120, sp+l*4, -sp, txY), placeholder="圖層名稱", readOnly=False)
		# 按鈕:
		self.w.button = vanilla.Button((sp, sp+l*5, -sp, btnY), "OK", callback=self.run_script) # 確定執行腳本

		# 開啟視窗並聚焦:
		self.w.open()
		self.w.makeKey()
		self.w.setDefaultButton(self.w.button)

		if not self.LoadPreferences():
			print("無法載入用戶偏好設定，將重置為預設值。")

	def checkboxCallback(self, sender):
		# 根据复选框的状态启用或禁用文本输入字段
		self.w.editText_5.enable(sender.get())
		# 保存复选框的新状态到用户偏好设置
		Glyphs.defaults["com.YinTzuYuan.SmartBBox.checkbox_5"] = sender.get()

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
			# NSUserDefaults.standardUserDefaults().registerDefaults_({
			# 	"com.YinTzuYuan.SmartBBox.editText_5": "Minimize", 
			# 	"com.YinTzuYuan.SmartBBox.editText_1": "Wilted",
			# 	"com.YinTzuYuan.SmartBBox.editText_2": "Flat",
			# 	"com.YinTzuYuan.SmartBBox.editText_3": "0",
			# 	"com.YinTzuYuan.SmartBBox.editText_4": "100",
			# 	"com.YinTzuYuan.SmartBBox.checkbox_5": False,
			# })
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


	def run_script(self, sender): # 執行腳本
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
			print("SmartBBox Error (run_script): %s" % e) # 錯誤回報
		

SmartBBox()

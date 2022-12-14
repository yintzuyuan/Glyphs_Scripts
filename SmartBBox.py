#MenuTitle: 智慧型部件編輯框
__doc__="""
自動新增圖層和配對智慧型部件長寬軸。
"""
# 自訂義參數
miniWidth_name = "Wilted" # 最窄圖層名稱
miniHeight_name = "Flat" # 最扁圖層名稱
miniNum_Value = 0 # 變化軸最小值
maxNum_Value = 1000 # 變化軸最大值

# 新增圖層部分

thisFont = Glyphs.font
currentMaster = thisFont.selectedFontMaster

for thisGlyph in [l.parent for l in thisFont.selectedLayers]:
	print("🔠 Processing %s" % thisGlyph.name)

	# 檢查是否有窄圖層
	all_layers = thisGlyph.layers
	for layer in all_layers:
		if layer.name == miniWidth_name:
			# 若有則終止新增動作
			print("已經存在" + miniWidth_name + "圖層。")
			break
	# 若沒有就新增一個窄圖層
	if layer.name != miniWidth_name:
		newLayer = GSLayer()
		newLayer = thisGlyph.layers[currentMaster.id].copy()
		newLayer.associatedMasterId = currentMaster.id
		newLayer.name = miniWidth_name
		print("新增圖層：%s" % newLayer.name)
		thisGlyph.layers.append(newLayer)

	# 檢查是否有扁圖層
	all_layers = thisGlyph.layers
	for layer in all_layers:
		if layer.name == miniHeight_name:
			# 若有則終止新增動作
			print("已經存在" + miniHeight_name + "圖層。")
			break
	# 若沒有就新增一個扁圖層
	if layer.name != miniHeight_name:
		newLayer = GSLayer()
		newLayer = thisGlyph.layers[currentMaster.id].copy()
		newLayer.associatedMasterId = currentMaster.id
		newLayer.name = miniHeight_name
		print("新增圖層：%s" % newLayer.name)
		thisGlyph.layers.append(newLayer)



# 增加智慧型部件軸

for layer in Font.selectedLayers:
	try:
		layer.parent.smartComponentAxes["Width"]
	except:
		# 寬度軸設定
		widthAxis = GSSmartComponentAxis()
		widthAxis.topValue = maxNum_Value # 設定軸最大值
		widthAxis.bottomValue = miniNum_Value # 設定軸最小值
		widthAxis.name = "Width"
		layer.parent.smartComponentAxes.append(widthAxis)
		smartWidthAxis = layer.parent.smartComponentAxes["Width"]

	try:
		layer.parent.smartComponentAxes["Height"]
	except:
		# 長度軸設定
		heightAxis = GSSmartComponentAxis()
		heightAxis.topValue = maxNum_Value # 設定軸最大值
		heightAxis.bottomValue = miniNum_Value # 設定軸最小值
		heightAxis.name = "Height"
		layer.parent.smartComponentAxes.append(heightAxis)
		smartHeightAxis = layer.parent.smartComponentAxes["Height"]

# 智慧型部件配對圖層; layers[0]: 數字代表圖層順序; 句尾數字 1 = 小, 2 = 大

	layer.parent.layers[0].smartComponentPoleMapping[smartWidthAxis.id] = 2 # Regular 寬度值設定
	layer.parent.layers[0].smartComponentPoleMapping[smartHeightAxis.id] = 2 # Regular 長度值設定
	layer.parent.layers[1].smartComponentPoleMapping[smartWidthAxis.id] = 1 # 窄圖層 寬度值設定
	layer.parent.layers[1].smartComponentPoleMapping[smartHeightAxis.id] = 2 # 窄圖層 長度值設定
	layer.parent.layers[2].smartComponentPoleMapping[smartWidthAxis.id] = 2 # 扁圖層 寬度值設定
	layer.parent.layers[2].smartComponentPoleMapping[smartHeightAxis.id] = 1 # 扁圖層 長度值設定

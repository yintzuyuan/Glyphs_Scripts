#MenuTitle: Smart BBox
__doc__="""
自動新增圖層和配對智慧型部件長寬軸。
"""

# 新增圖層部分

thisFont = Glyphs.font
currentMaster = thisFont.selectedFontMaster

for thisGlyph in [l.parent for l in thisFont.selectedLayers]:
	print("🔠 Processing %s" % thisGlyph.name)

	# 新增窄圖層
	newLayer = GSLayer()
	newLayer = thisGlyph.layers[currentMaster.id].copy()
	newLayer.associatedMasterId = currentMaster.id
	newLayer.name = "Wilted" # 編輯圖層名稱
	print("  Adding layer: %s" % newLayer.name)
	thisGlyph.layers.append(newLayer)

	# 新增扁圖層
	newLayer = GSLayer()
	newLayer = thisGlyph.layers[currentMaster.id].copy()
	newLayer.associatedMasterId = currentMaster.id
	newLayer.name = "Flat" # 編輯圖層名稱
	print("  Adding layer: %s" % newLayer.name)
	thisGlyph.layers.append(newLayer)



# 增加智慧型部件軸

for layer in Font.selectedLayers:
	try:
		layer.parent.smartComponentAxes["Width"]
	except:
		# 寬度軸設定
		widthAxis = GSSmartComponentAxis()
		widthAxis.topValue = 100 # 設定軸最大值
		widthAxis.bottomValue = 0 # 設定軸最小值
		widthAxis.name = "Width"
		layer.parent.smartComponentAxes.append(widthAxis)
		smartWidthAxis = layer.parent.smartComponentAxes["Width"]

	try:
		layer.parent.smartComponentAxes["Height"]
	except:
		# 長度軸設定
		heightAxis = GSSmartComponentAxis()
		heightAxis.topValue = 100 # 設定軸最大值
		heightAxis.bottomValue = 0 # 設定軸最小值
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


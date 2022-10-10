thisFont = Glyphs.font
currentMaster = thisFont.selectedFontMaster

for thisGlyph in [l.parent for l in thisFont.selectedLayers]:
	print("🔠 Processing %s" % thisGlyph.name)

	newLayer = GSLayer()
	newLayer = thisGlyph.layers[currentMaster.id].copy()
	newLayer.associatedMasterId = currentMaster.id
	newLayer.name = "Wilted"
	print("  Adding layer: %s" % newLayer.name)
	thisGlyph.layers.append(newLayer)

	newLayer = GSLayer()
	newLayer = thisGlyph.layers[currentMaster.id].copy()
	newLayer.associatedMasterId = currentMaster.id
	newLayer.name = "Flat"
	print("  Adding layer: %s" % newLayer.name)
	thisGlyph.layers.append(newLayer)



# Adding two interpolation axes to the glyph
for layer in Font.selectedLayers:
	try:
		layer.parent.smartComponentAxes["Width"]
	except:
		widthAxis = GSSmartComponentAxis()
		widthAxis.topValue = 100
		widthAxis.bottomValue = 0
		widthAxis.name = "Width"
		layer.parent.smartComponentAxes.append(widthAxis)
		smartWidthAxis = layer.parent.smartComponentAxes["Width"]

	try:
		layer.parent.smartComponentAxes["Height"]
	except:
		heightAxis = GSSmartComponentAxis()
		heightAxis.topValue = 100
		heightAxis.bottomValue = 0
		heightAxis.name = "Height"
		layer.parent.smartComponentAxes.append(heightAxis)
		smartHeightAxis = layer.parent.smartComponentAxes["Height"]


	layer.parent.layers[0].smartComponentPoleMapping[smartWidthAxis.id] = 2
	layer.parent.layers[0].smartComponentPoleMapping[smartHeightAxis.id] = 2
	layer.parent.layers[1].smartComponentPoleMapping[smartWidthAxis.id] = 1
	layer.parent.layers[1].smartComponentPoleMapping[smartHeightAxis.id] = 2
	layer.parent.layers[2].smartComponentPoleMapping[smartWidthAxis.id] = 2
	layer.parent.layers[2].smartComponentPoleMapping[smartHeightAxis.id] = 1

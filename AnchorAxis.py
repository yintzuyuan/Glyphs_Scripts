# MenuTitle: 根據錨點建立智慧組件軸
# -*- coding: utf-8 -*-
__doc__="""
此腳本會檢測主要圖層的錨點，並為尚未存在的錨點建立新圖層。同時，它會在所有現有圖層中添加這些新錨點。腳本還會為每個新錨點在智慧組件設定中建立屬性，使用完整的錨點名稱，並將其極端值設定為最大100、最小0。
"""

import GlyphsApp

font = Glyphs.font
glyph = font.selectedLayers[0].parent
mainLayer = glyph.layers[font.selectedFontMaster.id]

# 1. 偵測主要圖層的錨點
anchorNames = [a.name for a in mainLayer.anchors]

# 2. 檢查已存在的圖層名稱
existingLayerNames = [layer.name for layer in glyph.layers]

# 3. 複製新圖層並在所有圖層中添加新錨點
newAnchorNames = []
for anchorName in anchorNames:
    newLayerName = f"{mainLayer.name} {anchorName}"
    if newLayerName not in existingLayerNames:
        # 複製新圖層
        newLayer = mainLayer.copy()
        newLayer.name = newLayerName
        glyph.layers.append(newLayer)
        newAnchorNames.append(anchorName)
        
        # 在所有已存在的圖層中添加新錨點
        for layer in glyph.layers:
            if layer.name != newLayerName and not layer.anchors[anchorName]:
                newAnchor = GSAnchor()
                newAnchor.name = anchorName
                newAnchor.position = mainLayer.anchors[anchorName].position
                layer.anchors.append(newAnchor)
        
        print(f"已處理新錨點: {anchorName}")
    else:
        print(f"跳過已存在的圖層: {newLayerName}")

# 4 & 5 & 6. 新增智慧組件屬性並設定極端值（僅處理新增的錨點）
for anchorName in newAnchorNames:
    axis = GSSmartComponentAxis()
    
    # 使用完整的錨點名稱作為軸名稱
    axis.name = anchorName
    
    # 修改極端值
    axis.topValue = 100
    axis.bottomValue = 0
    glyph.smartComponentAxes.append(axis)
    
    # 保持 smartComponentPoleMapping 設定不變
    for layer in glyph.layers:
        if layer.name.endswith(f" {anchorName}"):
            layer.smartComponentPoleMapping[axis.id] = 1
        else:
            layer.smartComponentPoleMapping[axis.id] = 2

if newAnchorNames:
    print(f"已處理以下新錨點: {', '.join(newAnchorNames)}")
else:
    print("沒有新的錨點需要處理")

print("智慧組件設定完成!")
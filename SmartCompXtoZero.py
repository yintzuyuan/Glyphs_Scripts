#MenuTitle: 組件垂直居中
# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
__doc__="""
將選取字符的所有圖層中，智慧組件垂直對齊至中心點（座標軸x=0）。
"""
from GlyphsApp import *

myGlyph = Glyphs.font.selectedLayers[0].parent
for layer in myGlyph.layers:
	for component in layer.components:
		if component.position.x != 0:
			component.position = (0, component.position.y)
		else:
			pass
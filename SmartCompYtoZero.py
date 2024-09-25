# MenuTitle: 組件水平居中
# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
__doc__="""
將選取字符的所有圖層中，智慧組件水平對齊至中心點（座標軸y=0）。
"""
from GlyphsApp import *

myGlyph = Glyphs.font.selectedLayers[0].parent
for layer in myGlyph.layers:
	for component in layer.components:
		if component.position.y != 0:
			component.position = (component.position.x, 0)
		else:
			pass
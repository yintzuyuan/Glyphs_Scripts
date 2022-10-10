# Glyphs_Scripts

# 腳本安裝方法

1. 腳本->打開腳本檔案夾
2. 將`腳本.py`檔案丟進去。
3. 按住`option`點選 腳本->重新載入腳本
4. Done.

# SmartBBox - 智慧型部件自動化完成 <h1>

這兩天花了一些時間研究 Glyphs 的腳本語法，對於去年曾經提到智慧型部件設定繁瑣的問題終於解決了。在此分享一下我的解決歷程。

＝＝＝＝＝＝＝＝＝＝＝＝＝

這是我去年對於這個問題的發問影片 (https://youtu.be/A97dZtYgmAA) 總之就是為了製作可變形的智慧型部件需要新增圖層、為它們命名、設定軸屬性和配對圖層，太多繁瑣的步驟希望能透過腳本快速完成。

這是我在 Glyphs 論壇發問的主題：
https://forum.glyphsapp.com/t/about-the-height-and-width-values-of-smart-component/20402

＝＝＝＝＝＝＝＝＝＝＝＝＝

我把腳本拆成兩個部分解決，圖層部分以及智慧型部件設定的部分。

－－－－－－－－－－－－－

圖層部分我參考了 mekkablue 腳本集裡面的 Insert Layers 腳本（在 Interpolation 分類中），作者將選項寫成一套ＵＩ，我只截取了生成的部分改成符合自己需求的語法

mekkablue 腳本集：
https://github.com/mekkablue/Glyphs-Scripts

－－－－－－－－－－－－－

最後是智慧型部件設定的部分，起先我找到了官網提供的語法集，裡面確實提供了我需要的功能

設定軸屬性：
https://docu.glyphsapp.com/#GSGlyph.smartComponentAxes

配對圖層：
https://docu.glyphsapp.com/#GSLayer.smartComponentPoleMapping


但是設定軸屬性的部分，我複製了範例的語法卻在 Glyphs 中無法順利運行。於是我用語法中的幾個關鍵字在官方論壇中尋找，發現了這篇文章。

時間來到今年中，中國的設計師提出了相同的問題，或許是問題描述的比較完整所以得到了解決：
https://forum.glyphsapp.com/t/automate-script-for-layer-settings-of-smart-component/23011/6

裡面提供的語法成為我需要的腳本最後一塊拼圖，這個腳本終於能在未來的造字過程中成功幫我省下很多時間。

# 在 Unity 中使用 UI 素材

这些文件是 SVG 矢量图片，浏览器可以直接预览它们；它们不是网页代码。

## 推荐导入方式

1. 打开 Unity 的 `Window > Package Manager`。
2. 在 Unity Registry 中安装 `Vector Graphics` 包。
3. 回到 Project 面板，打开 `Assets/UI_Prototype/`。
4. 新建 Canvas：`GameObject > UI > Canvas`。
5. 在 Canvas 下新建空物体，点击 `Add Component`，添加 `SVG Image`。
6. 把 SVG 文件拖到 `SVG Image` 的 `Vector Graphic` 属性上。
7. 用 RectTransform 调整位置和大小。

## 文件用途

- `ui_theme.svg`：战斗 HUD 和升级卡的总视觉稿。
- `ui_components.svg`：暂停、设置、胜利、提示框等组件。
- `ui_icons.svg`：图标条。
- `ui_meta_screens.svg`：角色、武器、装备、图鉴和成长界面。
- `ui_results_and_world.svg`：结算、小地图、提示和加载界面。

## 注意

这些 SVG 中有些是组合素材图，适合做视觉参考或整张面板背景。要让每个按钮、血条、图标独立控制，需要把对应区域拆成独立 SVG，或者在 Unity 中使用 Sprite Editor 切图。

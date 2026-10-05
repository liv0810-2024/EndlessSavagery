# EndlessSavagery UI 使用说明

本文件夹中的 UI 资源采用暗黑奇幻、生存割草风格。实际制作 Unity Canvas 时，优先使用 `Parts` 和 `Icons` 文件夹中的独立资源；根目录下的整套 SVG 主要用于查看整体视觉方向。

## 一、推荐的 Canvas 层级

```text
Canvas
├── MainMenuPanel
├── GameplayHUD
│   ├── HealthBar
│   ├── ExperienceBar
│   ├── SkillSlots
│   ├── BossBar
│   └── EventToast
├── UpgradePanel
├── PausePanel
├── ResultPanel
└── SystemPopup
```

## 二、独立 UI 部件

### 1. `Parts/panel_main.svg`

主菜单的大型背景面板。

适用位置：

- 开始游戏
- 角色选择
- 武器选择
- 图鉴
- 设置

使用方式：放在 Canvas 下作为背景 Image，建议设置 `Image Type = Sliced`，用于承载按钮和标题。

### 2. `Parts/panel_gameplay.svg`

战斗中信息面板。

适用位置：

- 右上角战斗信息
- 生存时间
- 当前等级
- 击杀数量
- 金币数量

### 3. `Parts/bar_health.svg`

玩家生命条。

适用位置：玩家头像旁边或屏幕左上角。

建议结构：

```text
HealthBar
├── Background
└── Fill
```

生命值降低时，只缩放 Fill 的横向宽度。

### 4. `Parts/bar_xp.svg`

玩家经验条。

适用位置：屏幕上方或生命条下方。

经验满后触发升级三选一界面。

### 5. `Parts/bar_boss.svg`

Boss 或精英敌人的生命条。

适用位置：屏幕顶部中央。

只有 Boss 或精英敌人出现时显示，普通敌人不使用。

### 6. `Parts/slot_skill.svg`

技能槽背景。

适用位置：屏幕右下角或右侧技能栏。

建议每个技能槽再添加：

- 技能图标
- 冷却遮罩
- 技能等级数字
- 快捷键文字

### 7. `Parts/card_upgrade_red.svg`

红色攻击型升级卡。

适合：

- 攻击力提升
- 暴击率提升
- 近战伤害提升
- 火焰、流血等攻击效果

### 8. `Parts/card_upgrade_blue.svg`

蓝色能量型升级卡。

适合：

- 技能冷却缩短
- 能量上限提升
- 移动速度提升
- 冰冻、闪电等技能效果

### 9. `Parts/card_upgrade_gold.svg`

金色稀有升级卡。

适合：

- 稀有技能
- 武器进化
- 强力被动
- 传奇奖励

### 10. `Parts/panel_pause.svg`

暂停菜单背景。

建议放置按钮：

- 继续游戏
- 设置
- 返回主菜单

### 11. `Parts/panel_settings.svg`

设置面板背景。

建议放置设置项：

- 音乐音量
- 音效音量
- 画面质量
- 全屏开关
- 操作说明

### 12. `Parts/panel_victory.svg`

胜利界面背景。

适用条件：

- 完成关卡
- 击败 Boss
- 达到目标生存时间

建议按钮：继续、领取奖励、返回主菜单。

### 13. `Parts/panel_tooltip.svg`

通用说明框。

适用位置：

- 鼠标悬停提示
- 技能详情
- 装备详情
- 未解锁原因

### 14. `Parts/panel_chest.svg`

宝箱奖励面板。

适用位置：

- 宝箱开启
- 随机奖励
- 战斗结束奖励

面板中间放置宝箱动画或奖励图标。

### 15. `Parts/panel_result.svg`

战斗结算面板。

建议显示：

- 生存时间
- 击杀数量
- 获得金币
- 获得经验
- 解锁内容
- 再来一局

## 三、独立图标

位置：`Assets/UI_Prototype/Icons/`

### `icon_life.svg`

生命、治疗、生命上限提升。

### `icon_energy.svg`

能量、技能资源、技能冷却相关信息。

### `icon_time.svg`

生存时间、倒计时、限时挑战。

### `icon_shield.svg`

护盾、减伤、无敌状态、防御加成。

### `icon_warning.svg`

危险、Boss 出现、金币不足、未解锁提示。

## 四、根目录整图的用途

### `ui_theme.svg`

完整战斗 HUD 和升级卡的视觉总览。适合查看布局，不建议作为实际 UI 的单个 Image 使用。

### `ui_components.svg`

暂停、设置、胜利、提示和警告组件的组合预览。实际制作请使用 `Parts` 文件夹中的独立文件。

### `ui_meta_screens.svg`

角色、武器、装备、图鉴和局外成长的组合预览。

### `ui_results_and_world.svg`

结算、小地图、提示条和加载条的组合预览。

## 五、Unity 中的基本使用方式

1. 创建 Canvas：`GameObject > UI > Canvas`。
2. 创建图片：右键 Canvas，选择 `UI > Image`。
3. 在 Project 面板打开 `Assets/UI_Prototype/Parts/`。
4. 将对应 SVG 拖到 Image 的 `Source Image` 或 `Vector Graphic` 属性。
5. 通过 RectTransform 调整位置和大小。
6. 需要点击时，在 Image 上添加 Button 组件，或者创建 UI Button 并将这个图片作为按钮子物体。
7. 需要拉伸面板时，将 Image 的 `Image Type` 设置为 `Sliced`。

## 六、推荐制作顺序

1. `panel_main.svg`：先完成主菜单。
2. `bar_health.svg`、`bar_xp.svg`、`slot_skill.svg`：完成战斗 HUD。
3. `card_upgrade_red.svg`、`card_upgrade_blue.svg`、`card_upgrade_gold.svg`：完成升级界面。
4. `panel_pause.svg`、`panel_settings.svg`：完成暂停和设置。
5. `panel_result.svg`、`panel_victory.svg`：完成结算流程。
6. `Icons` 文件夹：给各个界面补充图标。

## 八、主页面和登录页面

### `Pages/page_main_menu.svg`

游戏启动后的主页面背景和菜单布局。使用时将它设置为 Canvas 下的全屏 Image，再叠加 `Parts/logo_endless_savagery.svg` 和按钮资源。

### `Pages/page_login.svg`

登录页面背景和登录面板。它包含用户名输入框、密码输入框、登录按钮、游客登录按钮和返回按钮的位置框架。输入框文字和按钮文字应使用 Unity UI Text 或 TextMeshPro 叠加。

### `Parts/logo_endless_savagery.svg`

游戏标题装饰。放在主页面或登录页面的上方中央。

### `Parts/button_primary.svg`

主要按钮，例如开始游戏、登录、确认。

### `Parts/button_secondary.svg`

次要按钮，例如设置、返回、取消。

### `Parts/button_danger.svg`

危险操作按钮，例如退出游戏、删除存档、放弃战斗。

### `Parts/input_field.svg`

用户名、密码等输入框背景。需要在上面叠加 Unity 的 Input Field 或 TMP Input Field 组件。

## 九、全部拆分资源位置

由于 Tuanjie 对 SVG Vector Sprite 不提供可用的 Sprite Editor 切割，实际使用时请打开：

`Assets/UI_Prototype/Split/`

该文件夹中的每个 SVG 都是独立资源，可以直接拖到 Image、Button、SVG Image 或 Sprite Renderer。`Parts`、`Icons` 和 `Pages` 文件夹中的资源同样已经是独立文件。

根目录中的 `ui_theme.svg`、`ui_components.svg`、`ui_meta_screens.svg` 和 `ui_results_and_world.svg` 只作为整套视觉参考，不需要再切割。

## 七、重要说明

Tuanjie 当前对 SVG 的 `Vector Sprite` 不支持使用 Sprite Editor 切割。因此这些资源已经按独立 SVG 文件提供。每个文件可以单独拖入 Image、Button 或 Sprite Renderer；不需要再对整图执行 Slice。

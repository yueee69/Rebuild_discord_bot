# Discord bot 重構專案

[舊版](https://github.com/yueee69/discord-bot)

## 🚩 專案背景
此專案和舊版的功能幾乎完全一樣，在於此版是利用OOP(物件導向設計)方式寫的。
因原版的架構是一次寫到底，可讀性、可修改性、可拓展性 基本可以說是沒有。
有幸與元智大學的資工系學長交流後，發現自己之前的設計架構存在嚴重缺陷，於是開始進行大規模的程式重構。

---

## ✨ 目前已完成的重構內容

- [x] 部分核心指令已拆解為獨立模組並進行程式重寫
- [x] 建立明確且易於維護的架構

---

## 📂 專案結構

```
discord-bot
├── callbacks                 # 依指令為單位，用於驅動UI交互後的回應
├── views                     # 依指令為單位，用於創建該指令會用到的所有視圖組件
├── commands/impl             # Discord 機器人指令模組
├── core/constants            # 用於存放各種字串、定數
├── events/                   # (開發中)用於監聽各種觸發事件(例如: on_message等)
├── features/                 # (開發中)此功能是用來實現自動購買的服務
├── Json/                     # 保留舊版的Json，只有重構內部的Json架構
├── Lottery/                  # 抽獎的驅動資料夾，由main_driver負責啟動各獎池的驅動器，大致架構利用了抽象、策略模式
├── models/                   # 將Json的檔案物件化(一個json為一個單位)
├── profile_management/       # 需要權限級指令的存放資料夾(更改暱稱、指定身分組、創建身分組)，包括main_driver
|   ├── drivers/              # 存放各種指令driver的資料夾，架構和pattern和Lottery差不多
│   ├── DiscordPermissionsTool/ #存放需要權限級操作的模塊(創建身分組、加派身分組、更改別人的暱稱等)
├── ranks/                    # 存放"排行榜"的模塊，這裡用到抽象模式，子類只需要初始化父類即可
└── main.py                   # 專案進入點
```

---

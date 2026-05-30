---
name: teaching-minigames
description: 教學素材小遊戲產生器。當使用者上傳教材（PDF、圖片、Word 文件等），請一定要使用此技能，自動分析每個重點並為每個重點製作一個形成性評量小遊戲，發佈為可分享的 HTML 網頁，附帶網址與 QR Code，供數位教學平台使用。觸發情境包含：「根據教材出小遊戲」、「幫我把教材做成小遊戲」、「教材轉互動測驗」、「幫我出形成性評量」、「教材有幾個重點就做幾個遊戲」、「製作可分享的測驗網頁」、「幫我做 QR Code 遊戲」等。即使使用者只說「上傳教材做遊戲」，也請使用此技能。
---

# Teaching Material Mini-Games Skill

將教材自動轉換為「一重點一小遊戲」的形成性評量網頁，附 QR Code 讓教師在任何數位平台快速使用。

---

## 整體工作流程

```
1. 分析教材 → 2. 提取重點清單（確認） → 3. 製作小遊戲 HTML
→ 4. 打包索引頁 → 5. 自動上傳 GitHub → 6. 啟用 GitHub Pages
→ 7. 回傳每個遊戲的網址 + QR Code
```

---

## Step 1：分析教材，提取重點

讀取使用者上傳的教材（PDF / 圖片 / .docx / 純文字）。
用以下框架萃取「學習重點（Key Learning Points）」：

- 每個重點 = 一個獨立、可測驗的知識單元
- 命名格式：`重點N：[簡短標題]`
- 建議數量：3～10 個（依教材密度決定）
- 每個重點附上：核心概念、2～4 個測驗素材（答案、干擾選項、例句等）

**在繼續前，先向使用者確認重點清單是否正確。**

---

## Step 2：選擇遊戲類型

根據每個重點的性質，從以下遊戲類型中挑選最合適的：

| 遊戲類型 | 適用情境 | 檔名 |
|---------|---------|------|
| 選擇題 (MCQ) | 概念理解、定義 | `game-mcq.html` |
| 填充題 (Fill-in-Blank) | 關鍵詞記憶、公式 | `game-fill.html` |
| 配對題 (Matching Pairs) | 詞彙對應、因果關係 | `game-match.html` |
| 是非題 (True/False) | 常見迷思澄清 | `game-tf.html` |
| 排序題 (Ordering) | 步驟、時序、流程 | `game-order.html` |
| 記憶翻牌 (Memory Cards) | 詞彙與圖像記憶 | `game-memory.html` |

每個重點可以使用不同類型，增加多樣性。

---

## Step 3：製作每個小遊戲 HTML

每個遊戲必須是**完全獨立的單一 HTML 檔案**，不依賴外部伺服器。

### HTML 結構規範

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[重點標題] - 小遊戲</title>
  <!-- 所有 CSS 內嵌於 <style> -->
</head>
<body>
  <!-- 遊戲內容 -->
  <!-- 所有 JS 內嵌於 <script> -->
</body>
</html>
```

### 必備 UI 元素

每個遊戲頁面都必須包含：
- **標題**：重點名稱
- **說明**：簡短遊戲規則（1 句話）
- **遊戲區域**：互動題目
- **即時回饋**：答對 ✅ 顯示鼓勵語，答錯 ❌ 顯示正確答案
- **得分/進度顯示**：例如「2 / 4 題」
- **重玩按鈕**

### 設計風格規範

- 手機優先（行動裝置友善）
- 字體大小 ≥ 16px
- 按鈕夠大（min-height: 44px）
- 配色使用高對比、清晰的教育風格
- 不使用任何外部 CDN（純內嵌，離線可用）

詳細各類型遊戲的 HTML 模板請參考：`references/game-templates.md`

---

## Step 4：製作總索引頁面

產生一個 `index.html`，作為所有小遊戲的入口：

- 列出所有重點與對應遊戲連結
- 顯示每個遊戲的 QR Code（使用 QR Code 嵌入方式，見下方）
- 可印出 / 投影給學生使用

---



---

## Step 5：QR Code 嵌入（在 HTML 內）

每個遊戲的 HTML 中嵌入會動態顯示自身 QR Code 的程式碼，讓使用者可在瀏覽器中直接顯示 QR Code：

```html
<div class="qr-section">
  <img id="qr-img" width="150" height="150" alt="QR Code">
  <p>掃描開啟此遊戲</p>
</div>
<script>
  // 發佈後自動顯示當前頁面的 QR Code
  document.getElementById('qr-img').src =
    'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data='
    + encodeURIComponent(window.location.href);
</script>
```

---

## Step 6：自動上傳至 GitHub 並發佈

**完整說明請參考：`references/github-publish.md`**

### 6-1. 收集必要資訊

先詢問使用者（若未提供）：
- **GitHub Personal Access Token**（需有 `repo` 權限）
- **GitHub 帳號名稱**
- **Repository 名稱**（預設：`teaching-games`，若不存在會自動建立）

### 6-2. 執行上傳腳本

使用 `bash_tool` 以 Python 腳本呼叫 GitHub REST API：

```bash
python3 /home/claude/github_upload.py \
  --token "$TOKEN" \
  --user "$GITHUB_USER" \
  --repo "$REPO_NAME" \
  --files-dir "/mnt/user-data/outputs/"
```

詳細腳本內容見 `references/github-publish.md` 的「完整上傳腳本（Python 版）」。

**Claude 應在執行前將此腳本寫入 `/home/claude/github_upload.py`。**

### 6-3. 啟用 GitHub Pages

上傳完成後自動呼叫 Pages API 啟用發佈。

### 6-4. 等待並確認

GitHub Pages 約需 **1～3 分鐘**上線。Claude 應告知使用者預計等待時間。

---

## Step 7：最終輸出

### 7-1. 輸出檔案

Claude 應輸出以下檔案到 `/mnt/user-data/outputs/`，並用 `present_files` 呈現：

```
outputs/
├── index.html              # 總索引頁（含所有 QR Code）
├── game-01-[重點名].html
├── game-02-[重點名].html
└── ...
```

### 7-2. 在對話中回傳網址與 QR Code

發佈成功後，**在對話訊息中**以 Markdown 格式顯示每個遊戲的資訊：

```markdown
## ✅ 已發佈至 GitHub Pages！

> ⏳ 若連結顯示 404，請等待 1～3 分鐘後重試。

---

### 📋 總索引頁
🔗 https://[user].github.io/[repo]/
![QR](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://[user].github.io/[repo]/)

---

### 重點 1：[標題]（選擇題）
🔗 https://[user].github.io/[repo]/game-01-xxx.html
![QR](https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https://[user].github.io/[repo]/game-01-xxx.html)

### 重點 2：[標題]（配對題）
🔗 ...
![QR](...)
```

---

## 品質檢查清單

製作完每個遊戲前，確認：
- [ ] HTML 語法正確，可在瀏覽器直接開啟
- [ ] 所有題目與答案來自教材，無幻覺
- [ ] 每個遊戲至少 3 題（建議 4～6 題）
- [ ] 答錯時顯示正確答案與說明
- [ ] 遊戲在手機上正常顯示
- [ ] QR Code 使用 `window.location.href`（動態，發佈後自動正確）
- [ ] 索引頁列出所有遊戲

上傳發佈後確認：
- [ ] GitHub Repo 已建立（或已存在）
- [ ] 所有 HTML 檔案已成功上傳
- [ ] GitHub Pages 已啟用
- [ ] 對話中顯示每個遊戲的網址與 QR Code 圖片
- [ ] 告知使用者 1～3 分鐘生效

---

## 注意事項

- **不要使用外部 JS/CSS CDN**：確保離線可用（學校網路常有限制）
- **語言**：遊戲界面語言跟隨教材語言（中文教材 → 中文遊戲）
- **題目準確性**：所有題目與答案必須忠實來自教材，不可自行編造
- **難度**：形成性評量為主，難度適中，著重記憶與理解層次（Bloom's Level 1-2）

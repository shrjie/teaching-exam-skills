---
name: teaching-minigames
description: >
  教學素材小遊戲產生器。當使用者上傳教材（PDF、圖片、Word 文件等），請一定要使用此技能，
  自動分析每個重點並為每個重點製作一個形成性評量小遊戲，發佈為可分享的 HTML 網頁，
  附帶網址與 QR Code，供數位教學平台使用。觸發情境包含：「根據教材出小遊戲」、
  「幫我把教材做成小遊戲」、「教材轉互動測驗」、「幫我出形成性評量」、
  「教材有幾個重點就做幾個遊戲」、「製作可分享的測驗網頁」、「幫我做 QR Code 遊戲」等。
  即使使用者只說「上傳教材做遊戲」，也請使用此技能。

  相容於 OpenCode / Claude Code / 其他支援 Agent Skills 規格的 agent。
---

# Teaching Material Mini-Games Skill

將教材自動轉換為「一重點一小遊戲」的形成性評量網頁，附 QR Code 讓教師在任何數位平台快速使用。

---

## 環境相容性

本技能**預設為 OpenCode 環境設計**，同時也相容於 Claude Code 與其他符合 Agent Skills 規格的 agent。

- 所有檔案路徑使用**相對路徑**（相對於目前工作目錄）
- 工具呼叫使用標準名稱：`bash`（取代 `bash_tool`）
- 跨平台相容：macOS / Linux / Windows 都能執行 GitHub API 流程

> ⚠️ **GitHub Token 安全**：執行 Step 6 之前，agent 必須明確詢問使用者索取 GitHub PAT。
> **不要**將 token 寫入任何被 commit 的檔案（建議存在 `.env` 或環境變數，agent 結束後使用者可撤銷 token）。

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

詳細各類型遊戲的 HTML 模板請參考：`references/game-templates.md`（與 SKILL.md 同目錄，用 `read` 工具讀取）

---

## Step 4：製作總索引頁面

產生一個 `index.html`，作為所有小遊戲的入口：

- 列出所有重點與對應遊戲連結
- 顯示每個遊戲的 QR Code（使用 QR Code 嵌入方式，見下方）
- 可印出 / 投影給學生使用

> **輸出位置**：所有 HTML 檔案**先存到工作目錄**（預設 `output/`），再上傳到 GitHub。

```bash
mkdir -p output
# 假設已產出 N 個 game-XX-*.html
ls output/
```

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

**完整說明請參考：`references/github-publish.md`**（GitHub Pages 自動發佈指南）

### 6-1. 收集必要資訊

**第一次執行時，agent 必須先詢問使用者**（不主動假設）：

> 「要自動發佈到 GitHub Pages，我需要您的：
> 1. **GitHub Personal Access Token**（PAT，需有 `repo` 權限）
> 2. **GitHub 帳號名稱（username）**
> 3. **Repository 名稱**（例如：`teaching-games`，若不存在會自動建立）
>
> Token 申請步驟：GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic) → Generate new token
> 需勾選的權限：`repo`（全選）
>
> ⚠️ Token 只會用於本次操作，不會寫入任何 commit 的檔案；建議透過環境變數（如 `GITHUB_TOKEN`）傳入，agent 結束後可至 GitHub 撤銷 token。」

### 6-2. 準備上傳腳本

**注意**：本 repo **未包含** `github_upload.py`。請將以下腳本存到工作目錄下（**不會被 commit**）：

```bash
mkdir -p output
```

> Agent 請以 `write` 工具將下列 Python 腳本存為 `output/github_upload.py`（不加入 git）：

```python
# output/github_upload.py — GitHub Pages 自動發佈腳本
import base64, json, subprocess, sys, time, argparse, os
from pathlib import Path

def github_api(method, endpoint, token, data=None):
    cmd = ["curl", "-s", "-X", method,
           "-H", f"Authorization: token {token}",
           "-H", "Accept: application/vnd.github+json",
           "-H", "Content-Type: application/json",
           f"https://api.github.com{endpoint}"]
    if data:
        cmd += ["-d", json.dumps(data)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return {}

def upload_file(token, user, repo, filepath, filename):
    with open(filepath, 'rb') as f:
        content = base64.b64encode(f.read()).decode()
    
    existing = github_api("GET", f"/repos/{user}/{repo}/contents/{filename}", token)
    sha = existing.get("sha")
    
    payload = {"message": f"Upload {filename}", "content": content}
    if sha:
        payload["sha"] = sha
    
    result = github_api("PUT", f"/repos/{user}/{repo}/contents/{filename}", token, payload)
    return "content" in result or "commit" in result

def publish_to_github(token, user, repo, html_files):
    base_url = f"https://{user}.github.io/{repo}"
    
    # 1. 建立 repo（若不存在）
    check = github_api("GET", f"/repos/{user}/{repo}", token)
    if "id" not in check:
        print(f"建立 repo: {user}/{repo}")
        github_api("POST", "/user/repos", token, {
            "name": repo, "private": False,
            "description": "Teaching Mini-Games - Auto-generated"
        })
        time.sleep(2)
    else:
        print(f"repo 已存在: {user}/{repo}")
    
    # 2. 上傳所有檔案
    for local_path, filename in html_files:
        success = upload_file(token, user, repo, local_path, filename)
        print(f"{'✅' if success else '❌'} {filename}")
    
    # 3. 啟用 GitHub Pages
    pages_result = github_api("POST", f"/repos/{user}/{repo}/pages", token,
                              {"source": {"branch": "main", "path": "/"}})
    if pages_result:
        print(f"Pages API 回應: {pages_result.get('message', 'OK')}")
    
    # 4. 等待 Pages 啟用
    time.sleep(3)
    pages_info = github_api("GET", f"/repos/{user}/{repo}/pages", token)
    pages_url = pages_info.get("html_url", base_url)
    
    return True, pages_url

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--files-dir", required=True, help="Directory containing HTML files")
    args = parser.parse_args()
    
    files_dir = Path(args.files_dir)
    html_files = [(str(p), p.name) for p in files_dir.glob("*.html")]
    
    if not html_files:
        print("❌ 找不到任何 .html 檔案")
        sys.exit(1)
    
    print(f"準備上傳 {len(html_files)} 個檔案到 {args.user}/{args.repo}")
    success, url = publish_to_github(args.token, args.user, args.repo, html_files)
    print(f"\n✅ 發佈完成：{url}")
```

### 6-3. 執行上傳

```bash
# 方式 A：環境變數（推薦）
export GITHUB_TOKEN="ghp_xxx..."
python3 output/github_upload.py \
  --token "$GITHUB_TOKEN" \
  --user "$GITHUB_USER" \
  --repo "$REPO_NAME" \
  --files-dir "output/"
```

```bash
# 方式 B：直接傳入（不建議，token 會出現在 process list）
python3 output/github_upload.py \
  --token "ghp_xxx..." \
  --user "username" \
  --repo "teaching-games" \
  --files-dir "output/"
```

### 6-4. 啟用 GitHub Pages

**注意**：上傳腳本內部已呼叫 `POST /pages` 啟用 GitHub Pages，若已啟用（409）會自動忽略。

若要手動啟用：

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/pages \
  -d '{"source": {"branch": "main", "path": "/"}}'
```

### 6-5. 等待並確認

GitHub Pages 約需 **1～3 分鐘**上線。Agent 應告知使用者預計等待時間，並提供 URL。

---

## Step 7：最終輸出

### 7-1. 本機輸出檔案

所有 HTML 檔案**保留在工作目錄的 `output/`**（不刪除），使用者可隨時離線使用：

```
output/
├── index.html              # 總索引頁（含所有 QR Code）
├── game-01-[重點名].html
├── game-02-[重點名].html
├── ...
└── github_upload.py        # 上傳腳本（建議加入 .gitignore）
```

### 7-2. 在對話中回傳網址與 QR Code

發佈成功後，**在對話訊息中**以 Markdown 格式顯示每個遊戲的資訊：

```markdown
## ✅ 已發佈至 GitHub Pages！

> ⏳ 若連結顯示 404，請等待 1～3 分鐘後重試。
> 📁 本機檔案位置：`./output/`

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
- [ ] 本機 `output/` 資料夾保留所有檔案（不刪除）

---

## 注意事項

- **不要使用外部 JS/CSS CDN**：確保離線可用（學校網路常有限制）
- **語言**：遊戲界面語言跟隨教材語言（中文教材 → 中文遊戲）
- **題目準確性**：所有題目與答案必須忠實來自教材，不可自行編造
- **難度**：形成性評量為主，難度適中，著重記憶與理解層次（Bloom's Level 1-2）
- **Token 安全**：
  - 絕對不要將 GitHub PAT commit 到 repo（建議 `output/github_upload.py` 加入 `.gitignore`）
  - 建議 agent 結束後由使用者至 GitHub 撤銷 token
  - 若使用環境變數傳入，agent 結束後記得 `unset GITHUB_TOKEN`
- **本機檔案**：所有 HTML 與上傳腳本**保留在工作目錄的 `output/`**，不要刪除（使用者可能想離線用）

# GitHub Pages 自動發佈指南

此文件說明如何透過 GitHub REST API 將小遊戲自動上傳並發佈至 GitHub Pages。

> **OpenCode 相容性**：本指南已更新為 OpenCode 相容版本，使用 `bash` 工具與相對路徑，適用於 macOS / Linux / Windows。
>
> **Token 安全提醒**：絕對不要將 GitHub PAT commit 到 repo。建議透過環境變數 `GITHUB_TOKEN` 傳入，agent 結束後使用者可至 GitHub 撤銷 token。

---

## 前置需求：取得 GitHub Token

Agent 第一次執行此流程時，**必須先詢問使用者**：

> 「要自動發佈到 GitHub Pages，我需要您的：
> 1. **GitHub Personal Access Token**（PAT）
> 2. **GitHub 帳號名稱（username）**
> 3. **Repository 名稱**（例如：`teaching-games`，若不存在會自動建立）
>
> Token 申請步驟：GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic) → Generate new token
> 需勾選的權限：`repo`（全選）
>
> ⚠️ Token 只會用於本次操作，不會寫入任何 commit 的檔案；建議透過環境變數 `GITHUB_TOKEN` 傳入。」

---

## API 流程（agent 使用 `bash` 執行）

### Step A：建立或確認 Repository

```bash
# 檢查 repo 是否存在
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME"
```

若回傳 404，則建立 repo：
```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.github.com/user/repos \
  -d "{\"name\": \"$REPO_NAME\", \"private\": false, \"description\": \"Teaching Mini-Games\"}"
```

### Step B：上傳每個 HTML 檔案

```bash
# 將檔案轉為 base64 並上傳（macOS 的 base64 不支援 -w，改用 tr 去除換行）
FILE_CONTENT=$(base64 "$FILE_PATH" | tr -d '\n')
FILE_NAME=$(basename "$FILE_PATH")

# 先檢查檔案是否已存在（取得 SHA）
SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/contents/$FILE_NAME" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('sha',''))" 2>/dev/null)

# 建立或更新檔案
if [ -z "$SHA" ]; then
  # 新建檔案
  curl -s -X PUT \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/contents/$FILE_NAME" \
    -d "{\"message\": \"Add $FILE_NAME\", \"content\": \"$FILE_CONTENT\"}"
else
  # 更新檔案（需提供 SHA）
  curl -s -X PUT \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/contents/$FILE_NAME" \
    -d "{\"message\": \"Update $FILE_NAME\", \"content\": \"$FILE_CONTENT\", \"sha\": \"$SHA\"}"
fi
```

### Step C：啟用 GitHub Pages

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/pages" \
  -d '{"source": {"branch": "main", "path": "/"}}'
```

若已啟用（回傳 409），忽略錯誤繼續。

### Step D：取得發佈網址

```bash
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/pages" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('html_url',''))"
```

網址格式：`https://$GITHUB_USER.github.io/$REPO_NAME/`

---

## 完整上傳腳本（Python 版，更穩定，跨平台）

> 完整腳本已內嵌於 `SKILL.md` Step 6-2。此處提供精簡版供參考。
> 腳本會存到 `output/github_upload.py`（建議加入 `.gitignore`）。

```python
# output/github_upload.py — GitHub Pages 自動發佈腳本
import base64, json, subprocess, sys, time, argparse
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
    """
    html_files: list of (local_path, filename) tuples
    Returns: (success, pages_url)
    """
    base_url = f"https://{user}.github.io/{repo}"
    
    # 1. 建立 repo（若不存在）
    check = github_api("GET", f"/repos/{user}/{repo}", token)
    if "id" not in check:
        github_api("POST", "/user/repos", token, {
            "name": repo, "private": False,
            "description": "Teaching Mini-Games - Auto-generated"
        })
        time.sleep(2)
    
    # 2. 上傳所有檔案
    for local_path, filename in html_files:
        success = upload_file(token, user, repo, local_path, filename)
        print(f"{'✅' if success else '❌'} {filename}")
    
    # 3. 啟用 GitHub Pages
    github_api("POST", f"/repos/{user}/{repo}/pages", token,
               {"source": {"branch": "main", "path": "/"}})
    
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
    parser.add_argument("--files-dir", required=True)
    args = parser.parse_args()
    
    files_dir = Path(args.files_dir)
    html_files = [(str(p), p.name) for p in files_dir.glob("*.html")]
    
    if not html_files:
        print("❌ 找不到任何 .html 檔案")
        sys.exit(1)
    
    success, url = publish_to_github(args.token, args.user, args.repo, html_files)
    print(f"\n✅ 發佈完成：{url}")
```

**使用方式**：

```bash
# 建議使用環境變數（推薦）
export GITHUB_TOKEN="ghp_xxx..."
python3 output/github_upload.py \
  --token "$GITHUB_TOKEN" \
  --user "$GITHUB_USER" \
  --repo "$REPO_NAME" \
  --files-dir "output/"
```

---

## QR Code 回傳格式

發佈成功後，agent 應以 Markdown 格式回傳每個遊戲的資訊：

```markdown
## ✅ 發佈成功！

**總索引頁**
🔗 https://username.github.io/repo-name/
![QR Code](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://username.github.io/repo-name/)

---

### 重點 1：[標題]（選擇題）
🔗 https://username.github.io/repo-name/game-01-xxx.html
![QR Code](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://username.github.io/repo-name/game-01-xxx.html)

### 重點 2：[標題]（配對題）
🔗 https://username.github.io/repo-name/game-02-xxx.html
![QR Code](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://username.github.io/repo-name/game-02-xxx.html)
```

---

## 錯誤處理

| 錯誤狀況 | 處理方式 |
|---------|---------|
| Token 無效（401）| 提示使用者重新產生 Token，確認有 `repo` 權限 |
| Repo 名稱衝突 | 自動在名稱後加 `-2`，或詢問使用者 |
| Pages 已啟用（409）| 忽略，繼續取得現有 Pages URL |
| 上傳失敗（單一檔案）| 重試一次，仍失敗則繼續其他檔案，最後列出失敗清單 |
| Pages URL 未就緒 | 告知使用者「約 1～3 分鐘後可存取，URL 為：...」|

---

## 注意事項

- GitHub Pages 啟用後約需 **1～3 分鐘**才能正式上線
- 若使用者已有同名 Repo，會直接更新檔案（不覆蓋其他現有檔案）
- Token 安全：
  - 絕對不要將 GitHub PAT commit 到 repo
  - 建議透過環境變數 `GITHUB_TOKEN` 傳入
  - Agent 結束後提醒使用者至 GitHub 撤銷 token
  - 若要使用 `base64 -w 0`（Linux）但環境是 macOS，改用 `base64 | tr -d '\n'`
- Free 帳號的 GitHub Pages 為公開網頁，請勿存放敏感內容
- 跨平台注意：macOS 的 `base64` 指令不支援 `-w` 參數，腳本已用 `tr -d '\n'` 替代

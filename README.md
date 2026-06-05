# 教學出題技能集（Teaching & Exam Skills）— OpenCode 相容版

一組可重用的 **Agent Skills**，專注於**國中數學命題、審題、幾何配圖與形成性評量小遊戲**。
每個技能皆為獨立資料夾，內含一份 `SKILL.md`（含 YAML frontmatter 描述觸發時機），可供 **OpenCode**、**Claude Code** 或任何支援 Agent Skills 規格的 AI agent 直接讀取使用。

> 所有技能皆以**繁體中文**設計，題目對齊修訂版 Bloom 認知層次。
>
> 這是 [`mathruffian-dot/teaching-exam-skills`](https://github.com/mathruffian-dot/teaching-exam-skills) 的 **OpenCode 相容性改寫版**：移除 Claude 沙箱環境的硬編碼路徑與專屬工具名稱，採用相對路徑與標準工具呼叫。

---

## ✨ 與原版差異

| 項目 | 原版 | 本版（OpenCode 相容） |
|------|------|---------------------|
| 路徑 | 硬編碼 `/mnt/skills/user/...`、`/home/claude/...` | **相對路徑**（`./output/`、`./exam_output/`）+ 自動偵測多安裝位置 |
| 工具呼叫 | `bash_tool`、`view`、`present_files`、`web_search` | **標準名稱** `bash`、`read`、`websearch` |
| `pip install` | 假設 Linux 容器，`--break-system-packages` | **跨平台**：`--user` (macOS) / `--break-system-packages` (Linux) / `venv` 備援 |
| 對 Claude 沙箱依賴 | `present_files` 直接提供下載 | 改為告知檔案路徑，由使用者自行開啟 |
| 與 `draw` 技能 | 硬編碼 `~/.claude/skills/draw/draw.py` | **改為可選**：無 `draw` 技能時優雅跳過 illustration 步驟 |
| 技能 frontmatter | 標明 Claude 觸發情境 | 加上「**相容於 OpenCode / Claude Code**」說明 |

---

## 📦 包含的技能

| 技能 | 用途 | 額外檔案 |
|------|------|----------|
| [`jh-math-exam`](skills/jh-math-exam/SKILL.md) | 國中數學段考出題與審題專家。設計七/八/九年級段考試題、審題、建立雙向細目表、Bloom 認知層次分析，產出標準版面的題目卷與答案卷。 | ⚠️ 需 `scripts/generate_exam_docx.py`（未隨本 repo 提供） |
| [`jh-math-context-questions`](skills/jh-math-context-questions/SKILL.md) | 國中數學「生活情境非選擇題」命題。結合時事／生活情境，產出 Bloom 應用／分析層次的兩小題式非選題（共五大題，含詳解），匯出 Word（數學式用 OMML 呈現）。 | ⚠️ 需 `scripts/generate_exam_docx.py`（未隨本 repo 提供） |
| [`jh-math-geometry`](skills/jh-math-geometry/SKILL.md) | 國中數學幾何圖形 SVG 產生器。三角形、四邊形、圓、坐標平面、立體圖、三角形三心等，可匯出 Word／PPT。可被出題技能呼叫配圖。 | `scripts/`、`references/` |
| [`teaching-minigames`](skills/teaching-minigames/SKILL.md) | 把教材重點轉成形成性評量小遊戲，發佈為可分享 HTML + QR Code。 | `references/`（上傳腳本需 agent 即時產出，見 SKILL.md） |

---

## 🚀 安裝與使用

### 安裝到 OpenCode / Claude Code（個人技能目錄）

OpenCode 與 Claude Code 都會自動讀取 `~/.claude/skills/` 目錄下的技能，所以**安裝方式相同**：

```bash
# 從 GitHub clone
git clone https://github.com/shrjie/teaching-exam-skills.git

# 複製到個人 skills 目錄
cp -r teaching-exam-skills/skills/* ~/.claude/skills/

# 或僅安裝特定技能
cp -r teaching-exam-skills/skills/jh-math-geometry ~/.claude/skills/
```

### OpenCode 自動載入位置

OpenCode 會依序從以下位置載入 skills：

1. **專案內**：`<project>/.claude/skills/`、`<project>/.opencode/skills/`、`<project>/.agents/skills/`
2. **個人全域**：`~/.claude/skills/`、`~/.opencode/skills/`、`~/.agents/skills/`

本 repo 內所有 SKILL.md 都有自動偵測腳本路徑的邏輯，不限於單一安裝位置。

### 觸發方式

安裝完成後，在 OpenCode chat 中直接說：

- 「幫我出七年級第一次段考數學題，範圍是翰林版 1-1 等差數列」
- 「幫我畫一個標出 ABCD 的平行四邊形」
- 「把這份教材做成小遊戲並發佈到 GitHub Pages」

OpenCode 會依 SKILL.md 的 frontmatter `description` 自動載入對應技能。

---

## ⚠️ 使用前注意（外部依賴）

| 技能 | 依賴 | 說明 |
|------|------|------|
| `jh-math-exam` | `scripts/generate_exam_docx.py` | **本 repo 未含**；請從原 Claude 環境取得，或自行以 `python-docx` 撰寫 |
| `jh-math-context-questions` | `scripts/generate_exam_docx.py` | **本 repo 未含**；同上 |
| `jh-math-context-questions` | `draw` 技能（gpt-image-2 生圖）| **本 repo 未含**，**且改為可選**：無此技能時僅跳過 illustration 步驟，產出純文字＋幾何圖的試卷 |
| `jh-math-exam` / `jh-math-context-questions` | Word 匯出 | 需要可輸出 `.docx`（OMML 數學式）的環境（`python-docx` + `lxml`） |
| `jh-math-geometry` | `cairosvg`、`python-docx`、`python-pptx` | macOS 需先 `brew install cairo pkg-config libffi`；或使用 Inkscape 備援 |
| `teaching-minigames` | GitHub Token | 發佈到 GitHub Pages 時需使用者自備 Personal Access Token（`repo` 權限）。Token 由使用者即時提供，建議透過 `GITHUB_TOKEN` 環境變數傳入，agent 結束後可至 GitHub 撤銷 |

### 缺腳本時的替代方案

- **無 `generate_exam_docx.py`**：技能會自動降級為「以 Markdown 格式輸出試卷草稿」，由使用者手動排版
- **無 `draw` 技能**：`illustration` 步驟自動跳過，產出試卷仍可正常使用（僅缺少情境氛圍圖）
- **無 `cairosvg`**：`svg_to_image.py` 會自動嘗試 Inkscape / Edge headless 備援

---

## 🛠️ 開發與貢獻

修改本 repo 時，請遵守以下規範：

1. **所有路徑使用相對路徑或環境變數**，禁止硬編碼 `/mnt/...`、`/home/...`、`C:/Users/...`
2. **工具呼叫使用標準名稱**：`bash`、`read`、`websearch`（不要用 `bash_tool`、`view`、`web_search`）
3. **`pip install` 寫法**：

   ```bash
   pip3 install --user --quiet package 2>/dev/null || \
     pip3 install --break-system-packages --quiet package
   ```

4. **Frontmatter 必要欄位**：`name`（lowercase + hyphen）、`description`（1-1024 字元）
5. **跨平台字型**：Pillow 渲染時偵測系統中文字型（macOS PingFang、Linux Noto CJK、Windows 微軟正黑體）

---

## 📄 授權

MIT License，詳見 [LICENSE](LICENSE)。歡迎自由使用與修改。

---

## 致謝

- 原始設計：[`mathruffian-dot/teaching-exam-skills`](https://github.com/mathruffian-dot/teaching-exam-skills)
- OpenCode 相容性改寫：[shrjie](https://github.com/shrjie)

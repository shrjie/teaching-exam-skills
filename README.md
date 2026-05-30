# 教學出題技能集（Teaching & Exam Skills）

一組可重用的 **Agent Skills**，專注於**國中數學命題、審題、幾何配圖與形成性評量小遊戲**。
每個技能皆為獨立資料夾，內含一份 `SKILL.md`（含 YAML frontmatter 描述觸發時機），可供 Claude Code 或任何支援 Agent Skills 規格的 AI agent 直接讀取使用。

> 所有技能皆以**繁體中文**設計，題目對齊修訂版 Bloom 認知層次。

---

## 📦 包含的技能

| 技能 | 用途 | 額外檔案 |
|------|------|----------|
| [`jh-math-exam`](skills/jh-math-exam/SKILL.md) | 國中數學段考出題與審題專家。設計七/八/九年級段考試題、審題、建立雙向細目表、Bloom 認知層次分析，產出標準版面的題目卷與答案卷。 | — |
| [`jh-math-context-questions`](skills/jh-math-context-questions/SKILL.md) | 國中數學「生活情境非選擇題」命題。結合時事／生活情境，產出 Bloom 應用／分析層次的兩小題式非選題（共五大題，含詳解），匯出 Word（數學式用 OMML 呈現）。 | — |
| [`jh-math-geometry`](skills/jh-math-geometry/SKILL.md) | 國中數學幾何圖形 SVG 產生器。三角形、四邊形、圓、坐標平面、立體圖、三角形三心等，可匯出 Word／PPT。可被出題技能呼叫配圖。 | `scripts/`、`references/` |
| [`teaching-minigames`](skills/teaching-minigames/SKILL.md) | 把教材重點轉成形成性評量小遊戲，發佈為可分享 HTML + QR Code。 | `references/` |

---

## 🚀 給其他 Agent 使用

這是一個**純技能資料夾**結構。最簡單的用法：

```bash
git clone https://github.com/mathruffian-dot/teaching-exam-skills.git
```

然後讓你的 agent 讀取對應的 `skills/<技能名>/SKILL.md`。每份 `SKILL.md` 的 frontmatter 都描述了觸發情境與操作步驟。

### 安裝到 Claude Code（個人技能目錄）

```bash
# macOS / Linux
cp -r teaching-exam-skills/skills/* ~/.claude/skills/

# Windows (PowerShell)
Copy-Item teaching-exam-skills/skills/* $HOME/.claude/skills/ -Recurse
```

---

## ⚠️ 使用前注意（外部依賴）

| 技能 | 依賴 | 說明 |
|------|------|------|
| `jh-math-context-questions` | `draw` 技能 | SKILL.md 內有寫死路徑 `C:/Users/mathr/.claude/skills/draw/draw.py`（gpt-image-2 生圖）。**本 repo 未含此腳本**；若不需配圖可忽略相關步驟，或自行替換為你的生圖工具。 |
| `jh-math-context-questions` / `jh-math-exam` | Word 匯出 | 需要可輸出 `.docx`（OMML 數學式）的環境。 |
| `jh-math-geometry` | Python | `scripts/` 內為 SVG 轉檔與插入 Word/PPT 的腳本，需 Python 環境。 |
| `teaching-minigames` | GitHub Token | 發佈到 GitHub Pages 時需使用者自備 Personal Access Token（`repo` 權限）。Token 由使用者即時提供，不會被儲存。 |

---

## 📄 授權

MIT License，詳見 [LICENSE](LICENSE)。歡迎自由使用與修改。

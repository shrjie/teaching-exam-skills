---
name: jh-math-exam
description: >
  國中數學段考出題與審題專家技能。當使用者需要為國中數學（七年級、八年級、九年級）設計段考試題、審核試題品質、
  建立雙向細目表、分析題目認知層次分佈，或產出完整格式的題目卷與答案卷時，請一定要使用此技能。
  觸發情境包含：「幫我出數學考題」、「審一下這份考卷」、「做雙向細目表」、「依Bloom分級檢查題目」、
  「產出國中數學試題」、「段考命題」、「數學考卷格式」等。
  此技能整合修訂版 Bloom 認知層次四級分類（記憶/理解/應用/分析）、雙向細目表格式，以及光武國中段考卷的標準版面規格。

  相容於 OpenCode / Claude Code / 其他支援 Agent Skills 規格的 agent。
---

# 國中數學段考命題審題技能

## 環境相容性

本技能**預設為 OpenCode 環境設計**，同時也相容於 Claude Code 與其他符合 Agent Skills 規格的 agent。

- 所有檔案路徑使用**相對路徑**（相對於目前工作目錄），不依賴 `/home/claude/`、`/mnt/` 等硬編碼位置
- 工具呼叫使用標準名稱：`bash`（取代 `bash_tool`）、`read`（取代 `view`）
- 跨平台 `pip install` 寫法（macOS 用 `--user`，Linux 容器用 `--break-system-packages`）

> ⚠️ **本技能依賴外部腳本**：`scripts/generate_exam_docx.py`（產出 Word 試卷）、`scripts/bloom_review.py`（審題報告）。
> 此 repo **未包含** 這些腳本（僅有 SKILL.md 規格說明）。如需實際產出 Word，請：
> 1. 從原始 Claude 環境取得腳本（聯絡原作者或自行移植）
> 2. 或自行以 `python-docx` 撰寫
> 3. 或將 Step 6 的 Word 產出步驟改為「產出 Markdown 試卷草稿」交由使用者手動排版
>
> 同樣地，reference 檔（`bloom-taxonomy.md`、`shuangxiang-table.md`、`exam-format.md`、`jh-math-curriculum.md`）亦**未包含**於本 repo，agent 應以內嵌於本 SKILL.md 的內容為主。

---

## 技能概覽

本技能支援兩種模式，協助教師完成國中數學段考的完整命題與審題流程：

**模式 A：出題模式**（全新命題）
1. 需求訪談 — 確認年級、範圍、題型、配分
2. 規劃雙向細目表 — 章節 × 認知層次比例
3. 生成題目 — 按 Bloom 四級分類產出
4. **幾何圖形渲染** — 若有幾何題，自動產生配圖 PNG（呼叫 `jh-math-geometry` 技能）
5. 格式輸出 — 題目卷、答案卷、雙向細目表（三份 Word），幾何圖自動插入對應位置

**模式 B：審題模式**（審核現有考卷）
1. 接收考卷 — 使用者貼入文字或上傳圖片/Word
2. 逐題審查 — 判定 Bloom 層次、section 歸屬、答案與題目品質
3. 輸出分級報告 — 顯示統計與偏差提示
4. 格式輸出 — 僅產出雙向細目表（一份 Word）

---

## 處理流程

### Step 1：需求確認（必做）

向使用者確認以下資訊（未提供則詢問）：

| 項目 | 說明 |
|------|------|
| 年級 | 七年級 / 八年級 / 九年級 |
| 學期 & 次別 | 第一學期第三次段考 等 |
| 考試範圍 | 章節名稱 + 版本（翰林版 / 康軒版 / 南一版） |
| 題型需求 | 選擇題幾題、非選擇題幾題、配分 |
| 難度目標 | 參考 Bloom 各級比例，或教師自訂 |
| 模式 | **A. 出題**（全新產出題目卷+答案卷+細目表） / **B. 審題**（審核現有考卷，只產細目表） |

---

### Step 2：建立雙向細目表

依下列結構規劃雙向細目表（內嵌於本 SKILL.md，無需讀取外部檔案）：

- **縱軸**：教材章節（依考試範圍列出各節名稱）
- **橫軸**：認知層次（記憶 / 理解 / 應用 / 分析）
- **細格**：分數（題數），例如 `6（2）`

**段考建議比例**（來自 Bloom 分級專家設定）：

| 層次 | 定義 | 建議佔比 |
|------|------|---------|
| 第1級：記憶 | 回憶公式、定義、術語 | 10% |
| 第2級：理解 | 解釋、歸納、辨別差異 | 20% |
| 第3級：應用 | 帶入具體情境計算、解方程式 | 40% |
| 第4級：分析 | 多步驟推理、辨析結構關係 | 30% |

> ⚠️ 若偏離此比例超過 ±10%，需提醒調整。

---

### Step 3：題目生成（出題模式 A 專用）

依雙向細目表各格生成題目，每題須標註：
- 題號、題型（選擇 / 非選擇）
- Bloom 等級與判定關鍵理由
- 正確答案 + 解題過程
- **幾何圖形需求**（若題目需要圖，填寫 `geometry` 欄位，見下方 JSON 規格）

**各層次出題原則**：

- **第1級（記憶）**：辨認公式正確性、回憶定義，例如「下列何者是一元一次方程式？」
- **第2級（理解）**：解釋步驟、辨別差異，例如「下列哪一步驟開始發生錯誤？」
- **第3級（應用）**：給定具體數值/情境，帶公式計算，例如「某商店打折問題，求原價」
- **第4級（分析）**：多條件整合、推論隱含關係，例如「已知多個方程組，求某變數關係」

**選擇題格式規範**：
- 四選一（A/B/C/D），每題必須提供完整四個選項
- 干擾選項需具學習意義（常見錯誤）
- 每題明確有唯一正確答案

**答案分佈規則（必須嚴格遵守）**：
- 答案必須平均分佈於 A、B、C、D 四個選項，每個選項出現次數應大致相等（±1題以內）
- 例如：16 題選擇題 → A、B、C、D 各出現 4 次
- **禁止連續兩題答案相同**（例如：第3題答A，第4題不得再答A）
- 命題完成後，**必須自我檢查**答案序列，確認無連續重複，並確認各選項出現次數平衡

**答案分佈自我檢查表**（完成命題後填寫）：

```
答案序列：題1=?, 題2=?, 題3=?, ...（列出全部）
A 出現 _ 次｜B 出現 _ 次｜C 出現 _ 次｜D 出現 _ 次
是否有連續重複：□ 無 □ 有（需修正）
```

**非選擇題格式規範**：
- 需有完整的解題過程要求
- 分為多個子題 (1)(2)(3)，各子題標明配分
- 建議最後一題為情境應用題（第3-4級）

---

### Step 4：認知層次審查（審題模式 B 專用）

> **觸發條件**：使用者提供已出好的考卷（貼入文字、上傳圖片或 .docx），要求審題或產雙向細目表。

#### 4-1 接收考卷資訊

向使用者確認以下資訊（若考卷內已有則自動提取，不需重複詢問）：

| 項目 | 說明 |
|------|------|
| 年級 | 七年級 / 八年級 / 九年級 |
| 學期 & 次別 | 第一學期第一次段考 等 |
| 考試範圍 | 章節名稱（用於 section 歸屬） |
| 配分規則 | 選擇題每題幾分、各大題配分 |

#### 4-2 逐題審查

對每道題目判定：
- **section**：歸屬哪個節次（如「1-1 等差數列」），依考試範圍的章節名稱填寫
- **bloom_level**：第1~4級，填寫完整格式如「第3級（應用）」
- **品質檢查**：題目是否清晰、選項是否有意義、非選題是否合理

**審查輸出格式（在對話中顯示）**：

```
[題目審查報告]

題號 | 題目摘要（20字以內）  | section      | 判定層次   | 判定理由
-----|----------------------|-------------|-----------|------------------
01   | 辨認等差數列公差       | 1-1 等差數列 | 第1級（記憶）| 僅需辨認定義特徵
02   | 代入首項公差求第n項    | 1-1 等差數列 | 第3級（應用）| 給定數值帶公式計算
...

[統計摘要]
各節次題數：1-1 等差數列 X題 / 1-2 等差級數 X題 / ...
Bloom 分佈：1級 __%、2級 __%、3級 __%、4級 __%
建議比例：1級 10%、2級 20%、3級 40%、4級 30%
△ 差異提示：[若偏離 ±10% 則列出調整建議]
[品質問題]：[若有問題題目，列出題號與說明]
```

#### 4-3 整理為審題 JSON

審查完成後，將考卷資訊整理為審題 JSON，**儲存在工作目錄下**（預設 `exam_data.json`）：

```bash
mkdir -p exam_output
```

> 審題模式不需填寫 `answer`、`solution`（可留空字串），重點在 `section` 與 `bloom_level`。
> 非選擇題的 `sub_questions` 每小題**必須填入 `bloom_level` 與 `points`**，才能正確計入細目表。
> **審題模式必須額外填寫 `review_report` 欄位**（見下方格式）。

**`review_report` 欄位格式（加在 JSON 最外層）**：

```json
"review_report": {
  "mc_rows": [
    {
      "number": 1,
      "summary": "辨認等差數列公差",
      "section": "1-1 等差數列",
      "bloom_level": "第1級（記憶）",
      "answer": "C",
      "reason": "僅需辨認定義特徵"
    }
  ],
  "open_rows": [
    {
      "big_number": 1,
      "label": "(1)",
      "summary": "代入首項公差求第n項",
      "section": "1-1 等差數列",
      "bloom_level": "第3級（應用）",
      "points": 4,
      "reason": "給定具體數值帶公式計算"
    }
  ],
  "section_stats": [
    { "section": "1-1 等差數列", "mc_pts": 20, "open_pts": 5, "total": 25 }
  ],
  "bloom_stats": {
    "第1級（記憶）": { "pts": 10, "pct": 10, "suggest": 10 },
    "第2級（理解）": { "pts": 20, "pct": 20, "suggest": 20 },
    "第3級（應用）": { "pts": 40, "pct": 40, "suggest": 40 },
    "第4級（分析）": { "pts": 30, "pct": 30, "suggest": 30 }
  },
  "quality_issues": [
    {
      "type": "error",
      "title": "配分說明有誤（需修正）",
      "description": "說明欄寫「1-16題每題4分，15-21題每題3分」，應為「17-21題每題3分」。"
    }
  ]
}
```

#### 4-4 執行腳本（審題模式，產出雙向細目表 + 審題報告）

> ⚠️ **以下腳本需要 `generate_exam_docx.py`**，本 repo 未包含。若無法取得，請改用 Markdown 輸出（見替代方案）。

```bash
# 找腳本目錄（自動偵測安裝位置）
SKILL_SCRIPTS=""
for d in \
  "./skills/jh-math-exam/scripts" \
  "$HOME/.claude/skills/jh-math-exam/scripts" \
  "$HOME/.opencode/skills/jh-math-exam/scripts" \
  "$HOME/.agents/skills/jh-math-exam/scripts" \
  "/tmp/jh-math-exam/scripts"; do
  if [ -f "$d/generate_exam_docx.py" ]; then
    SKILL_SCRIPTS="$d"
    break
  fi
done

if [ -z "$SKILL_SCRIPTS" ]; then
  echo "❌ 找不到 generate_exam_docx.py，請安裝完整 jh-math-exam 腳本"
  exit 1
fi

# 安裝 python-docx
pip3 install --user --quiet python-docx lxml 2>/dev/null || \
  pip3 install --break-system-packages --quiet python-docx lxml

mkdir -p exam_output

# 審題模式加 --blueprint-only，產出雙向細目表與審題報告（兩份）
python3 "$SKILL_SCRIPTS/generate_exam_docx.py" exam_data.json exam_output/ --blueprint-only

GRADE=$(python3 -c "import json; d=json.load(open('exam_data.json')); print(d['grade'])")
EN=$(python3 -c "import json; d=json.load(open('exam_data.json')); print(d['exam_number'])")
echo "📄 雙向細目表：exam_output/${GRADE}數學第${EN}次段考_雙向細目表.docx"
[ -f "exam_output/${GRADE}數學第${EN}次段考_審題報告.docx" ] && \
  echo "📄 審題報告：exam_output/${GRADE}數學第${EN}次段考_審題報告.docx"
echo "✅ 完成"
```

**替代方案（無 `generate_exam_docx.py` 時）**：

以 Markdown 格式在對話中直接輸出：
- 雙向細目表（Markdown 表格）
- 審題報告（包含統計、差異提示、品質問題）

使用者可手動複製到 Word，或用其他工具轉檔。

---

### Step 5：整理為 JSON 資料

將所有題目整理為以下格式，**儲存在工作目錄下**（預設 `exam_data.json`）：

#### ▶ geometry 欄位說明（出題模式專用）

若題目需要幾何圖形配圖，在該題加入 `geometry` 欄位；不需要圖形則設為 `null`。

**幾何圖形 spec 對照（常用類型快速複製）**：

| 題目類型 | geometry.spec.type | 常用 subtype |
|---------|-------------------|-------------|
| 直角三角形 | `triangle` | `right` |
| 等腰三角形 | `triangle` | `isosceles` |
| 一般三角形 | `triangle` | `general` |
| 平行四邊形 | `quadrilateral` | `parallelogram` |
| 梯形 | `quadrilateral` | `trapezoid` |
| 圓（弦弧切） | `circle` | — |
| 坐標平面 | `coordinate_plane` | — |
| 角柱/角錐 | `solid_3d` | `rectangular_prism` / `cone` 等 |
| 平行線截角 | `parallel_lines` | — |

> 完整參數見本 SKILL.md 末尾「幾何圖形參數速查（內嵌）」章節

**JSON 格式（含 geometry 欄位）**：

```json
{
  "school_year": "114",
  "semester": "1",
  "exam_number": "3",
  "grade": "七年級",
  "scope": "翰林版第一冊第一章～第二章",
  "total_pages": 2,
  "mc_scoring": "1~7題每題4分、8~16題每題3分，共85分",
  "mc_questions": [
    {
      "number": 1,
      "section": "1-1 等差數列",
      "bloom_level": "第3級（應用）",
      "question": "如圖，△ABC 中，∠C = 90°，AC = 3，BC = 4，則 AB = ？",
      "options": { "A": "5", "B": "6", "C": "7", "D": "8" },
      "answer": "A",
      "solution": "由畢氏定理 AB² = AC² + BC² = 9 + 16 = 25，AB = 5",
      "geometry": {
        "caption": "圖一",
        "spec": {
          "type": "triangle",
          "config": {
            "subtype": "right",
            "vertex_labels": ["A", "B", "C"],
            "right_angle_at": "C",
            "side_labels": {"AC": "3", "BC": "4", "AB": "?"}
          },
          "canvas": {"width": 250, "height": 200}
        }
      }
    },
    {
      "number": 2,
      "section": "1-2 等差級數",
      "bloom_level": "第2級（理解）",
      "question": "不需要圖的題目範例",
      "options": { "A": "", "B": "", "C": "", "D": "" },
      "answer": "B",
      "solution": "",
      "geometry": null
    }
  ],
  "open_questions": [
    {
      "number": 1,
      "section": "1-2 等差級數",
      "total_points": 10,
      "context": "如圖，梯形 ABCD 中，AD∥BC，AD = 6，BC = 10，高為 4。",
      "geometry": {
        "caption": "圖二",
        "spec": {
          "type": "quadrilateral",
          "config": {
            "subtype": "trapezoid",
            "vertex_labels": ["A", "B", "C", "D"],
            "side_labels": {"AD": "6", "BC": "10"},
            "show_height": true,
            "height_label": "4"
          },
          "canvas": {"width": 280, "height": 220}
        }
      },
      "sub_questions": [
        {
          "label": "(1)",
          "bloom_level": "第3級（應用）",
          "points": 4,
          "question": "求梯形 ABCD 的面積。",
          "answer": "32",
          "solution": "面積 = (AD + BC) × 高 ÷ 2 = (6 + 10) × 4 ÷ 2 = 32"
        }
      ]
    }
  ]
}
```

> **注意**：`geometry` 欄位可放在 `mc_questions` 的每題，也可放在 `open_questions` 的大題 context 層級（整題共用一圖），或子題層級（每小題有各自的圖）。

---

### Step 5.5：幾何圖形渲染（若 JSON 中有 geometry 欄位）

**判斷是否需要執行**：掃描 `exam_data.json`，若任何題目的 `geometry` 欄位不為 `null`，則執行本步驟。

呼叫 `jh-math-geometry` 技能自動偵測腳本位置並渲染：

```bash
# 0. 找幾何技能腳本
GEOM_DIR=""
for d in \
  "./skills/jh-math-geometry" \
  "$HOME/.claude/skills/jh-math-geometry" \
  "$HOME/.opencode/skills/jh-math-geometry" \
  "$HOME/.agents/skills/jh-math-geometry" \
  "/Users/huangshrjie/Downloads/opencode/teaching-exam-skills/skills/jh-math-geometry" \
  "/tmp/jh-math-geometry"; do
  if [ -f "$d/scripts/geometry_renderer.py" ]; then
    GEOM_DIR="$d"
    break
  fi
done
if [ -z "$GEOM_DIR" ]; then
  echo "❌ 找不到 jh-math-geometry 腳本，請先安裝該技能"
  exit 1
fi
echo "幾何腳本目錄：$GEOM_DIR"

# 1. 安裝 cairosvg
pip3 install --user --quiet cairosvg 2>/dev/null || \
  pip3 install --break-system-packages --quiet cairosvg

# 2. 從 exam_data.json 提取所有 geometry spec
mkdir -p exam_output/geometry

python3 - <<PYEOF
import json
import os

exam = json.load(open('exam_data.json', encoding='utf-8'))
figures = []

def collect(q, prefix):
    geo = q.get('geometry')
    if geo and geo.get('spec'):
        spec = dict(geo['spec'])
        spec['id'] = f"{prefix}_fig"
        spec.setdefault('canvas', {'width': 260, 'height': 210})
        figures.append({
            'id': spec['id'],
            'type': spec['type'],
            'config': spec.get('config', {}),
            'canvas': spec['canvas'],
            '_caption': geo.get('caption', ''),
            '_question_key': prefix
        })

for q in exam.get('mc_questions', []):
    collect(q, f"mc_{q['number']}")

for q in exam.get('open_questions', []):
    collect(q, f"open_{q['number']}")
    for sq in q.get('sub_questions', []):
        label = sq['label'].strip('()')
        collect(sq, f"open_{q['number']}_{label}")

if figures:
    spec_data = {
        'figures': [{'id': f['id'], 'type': f['type'], 'config': f['config'], 'canvas': f['canvas']} for f in figures],
        'options': {'format': 'png', 'dpi': 150}
    }
    json.dump(spec_data, open('exam_output/geometry_spec.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    mapping = {f['id']: {'caption': f['_caption'], 'question_key': f['_question_key']} for f in figures}
    json.dump(mapping, open('exam_output/geometry_mapping.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"✅ 需要渲染 {len(figures)} 張幾何圖形")
else:
    print("ℹ️ 本份考卷無幾何圖形，跳過渲染")
PYEOF

# 3. 渲染（若有圖形）
if [ -f exam_output/geometry_spec.json ]; then
  python3 "$GEOM_DIR/scripts/geometry_renderer.py" \
      exam_output/geometry_spec.json \
      exam_output/geometry/
  echo "✅ 幾何圖形渲染完成："
  ls exam_output/geometry/*.png 2>/dev/null || echo "（無 PNG 輸出）"
fi
```

> **視覺確認**：用 `read` 工具查看 `exam_output/geometry/*.svg`，確認圖形正確再繼續。若圖形有誤，修改 `exam_data.json` 中對應的 `geometry.spec.config`，重新執行 Step 5.5。

---

### Step 6：匯出 Word 文件（必做）

JSON 整理完成後，執行以下腳本（同時產出題目卷與答案卷）：

> ⚠️ **此步驟需要 `generate_exam_docx.py` 腳本**，本 repo 未包含。如無法取得，請改用 Markdown 輸出（見替代方案）。

```bash
# Step 6-1：找腳本目錄
SKILL_SCRIPTS=""
for d in \
  "./skills/jh-math-exam/scripts" \
  "$HOME/.claude/skills/jh-math-exam/scripts" \
  "$HOME/.opencode/skills/jh-math-exam/scripts" \
  "$HOME/.agents/skills/jh-math-exam/scripts" \
  "/tmp/jh-math-exam/scripts"; do
  if [ -f "$d/generate_exam_docx.py" ]; then
    SKILL_SCRIPTS="$d"
    break
  fi
done

if [ -z "$SKILL_SCRIPTS" ]; then
  echo "❌ 找不到 generate_exam_docx.py，請安裝完整 jh-math-exam 腳本"
  echo "   替代方案：以 Markdown 格式輸出試卷草稿"
  exit 1
fi

# Step 6-2：安裝相依套件
pip3 install --user --quiet python-docx lxml 2>/dev/null || \
  pip3 install --break-system-packages --quiet python-docx lxml

# Step 6-3：產生文件
mkdir -p exam_output
python3 "$SKILL_SCRIPTS/generate_exam_docx.py" exam_data.json exam_output/

GRADE=$(python3 -c "import json; d=json.load(open('exam_data.json')); print(d['grade'])")
EN=$(python3 -c "import json; d=json.load(open('exam_data.json')); print(d['exam_number'])")
echo "📄 題目卷：exam_output/${GRADE}數學第${EN}次段考_題目卷.docx"
echo "📄 答案卷：exam_output/${GRADE}數學第${EN}次段考_答案卷（教師版）.docx"
echo "📄 雙向細目表：exam_output/${GRADE}數學第${EN}次段考_雙向細目表.docx"
echo "✅ Word 初稿產出完成"
```

#### Step 6.5：將幾何圖形插入題目卷（若有幾何圖）

若 Step 5.5 有產出幾何圖形，執行以下後處理腳本，將 PNG 插入對應題目後方：

```bash
if [ ! -f exam_output/geometry_mapping.json ]; then
  echo "ℹ️ 無幾何圖形，跳過插入步驟"
else
  python3 - <<PYEOF
import json, sys, re
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import sys
sys.path.insert(0, "$GEOM_DIR/scripts")
from insert_to_docx import insert_figure

exam   = json.load(open('exam_data.json',    encoding='utf-8'))
mapping = json.load(open('exam_output/geometry_mapping.json', encoding='utf-8'))
grade  = exam['grade']
en     = exam['exam_number']

docx_path = f"exam_output/{grade}數學第{en}次段考_題目卷.docx"
doc = Document(docx_path)

para_index = {}
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    m = re.match(r'^(\d{1,2})[\.．]', text)
    if m:
        key = f"mc_{m.group(1)}"
        para_index.setdefault(key, i)

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if '如圖' in text or '右圖' in text or '下圖' in text:
        for back in range(1, 4):
            if i - back >= 0:
                prev = doc.paragraphs[i - back].text.strip()
                m = re.match(r'^(\d{1,2})[\.．]', prev)
                if m:
                    key = f"mc_{m.group(1)}"
                    para_index.setdefault(key, i)
                    break

insertions = []
for fig_id, info in mapping.items():
    png_path = Path(f"exam_output/geometry/{fig_id}.png")
    if not png_path.exists():
        print(f"⚠️ 找不到圖形：{png_path}")
        continue
    qkey = info['question_key']
    caption = info.get('caption', '')
    if qkey in para_index:
        insertions.append((para_index[qkey], png_path, caption))
    else:
        print(f"⚠️ 找不到題號段落 {qkey}，圖形將插在文件末尾")
        insertions.append((len(doc.paragraphs) - 1, png_path, f"[{qkey}] {caption}"))

insertions.sort(key=lambda x: -x[0])

for para_idx, png_path, caption in insertions:
    from docx.oxml.ns import qn
    from copy import deepcopy
    import lxml.etree as etree

    img_para = doc.add_paragraph()
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = img_para.add_run()
    run.add_picture(str(png_path), width=Cm(5.5))

    if caption:
        cap_para = doc.add_paragraph(caption)
        cap_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in cap_para.runs:
            r.font.size = Pt(9)
            r.font.italic = True

    target_el = doc.paragraphs[para_idx]._element
    img_el = img_para._element

    if caption:
        cap_el = cap_para._element
        target_el.addnext(cap_el)
        target_el.addnext(img_el)
    else:
        target_el.addnext(img_el)

    print(f"✅ 已插入 {png_path.name} 於段落 {para_idx} 之後")

doc.save(docx_path)
print(f"✅ 幾何圖形插入完成：{docx_path}")
PYEOF
fi
```

**完成後，向使用者提供**：
- 圖片檔：`./exam_output/geometry/*.png`
- Word 檔：
  - `./exam_output/<grade>數學第<en>次段考_題目卷.docx`
  - `./exam_output/<grade>數學第<en>次段考_答案卷（教師版）.docx`
  - `./exam_output/<grade>數學第<en>次段考_雙向細目表.docx`

> OpenCode 環境下，使用者可直接從檔案總管開啟 `exam_output/` 目錄下載，或在 chat 介面用 `read` 工具預覽。

---

## 數學標記語法（題目撰寫規則）

在題目文字中，用大括號 `{}` 包住數學式，系統會自動轉為 Word OMML 格式正確顯示：

| 標記語法 | 說明 | 範例 |
|---------|------|------|
| `{x^2}` | x 的平方（上標） | x² |
| `{x^{n+1}}` | 上標含運算式 | x^(n+1) |
| `{x_1}` | x 下標 1 | x₁ |
| `{sqrt(2)}` | 根號 2 | √2 |
| `{sqrt[3](8)}` | 三次方根 | ∛8 |
| `{frac(3,4)}` | 分數 3/4 | ¾ |
| `{(a+b)/2}` | 含運算式的分數 | (a+b)/2 |
| `{\|x-3\|}` | 絕對值 | \|x-3\| |
| `{<=}` | 小於等於符號 | ≤ |
| `{>=}` | 大於等於符號 | ≥ |
| `{!=}` | 不等於符號 | ≠ |
| `{a*b}` | 乘號 | a×b |

> **提醒**：簡單的文字方程式（如 `2x + 3 = 7`）不需加 `{}`，保持普通文字即可。

---

## 快速參考：內容位置

| 需要什麼 | 在哪裡 |
|----------|------|
| Bloom 四級詳細準則、關鍵字、出題原則 | 本 SKILL.md Step 3（內嵌）|
| 雙向細目表格式規範 | 本 SKILL.md Step 2（內嵌）|
| 題目卷 / 答案卷版面格式 | 本 SKILL.md Step 6（內嵌 JSON 規格）|
| 108課綱三年數學完整章節、學習內容代碼 | 依使用者提供的考試範圍即時查詢；本 repo 未含 `jh-math-curriculum.md` |
| 幾何圖形完整參數 + 快速複製範例 | 見本 SKILL.md 末尾「幾何圖形參數速查（內嵌）」章節 |

> **何時查詢課綱內容**：確認考試範圍的學習內容代碼、撰寫雙向細目表的「對應課綱」欄位、或題目需與特定學習表現對齊時，使用 `websearch` 查詢「十二年國教 108 課綱 國中數學 學習內容」對應學期。

---

## 注意事項

- 數學式一律使用 `{}` 標記，不使用 x^2 或 √ 等文字替代
- 情境題（第3-4級）應與日常生活掛鉤，情境需真實合理
- 選擇題選項不得出現「以上皆是」或「以上皆非」
- 非選擇題每小題配分需明確標示於 `points` 欄位
- 解題過程（`solution`）請用換行分隔每個步驟，方便排版
- **【答案分佈】** 選擇題答案必須平均分佈於 A/B/C/D，且禁止連續兩題答案相同。整份 JSON 的 `mc_questions` 填寫完後，必須重新審查 `answer` 欄位序列，若有連續重複或嚴重不均，立即調整該題答案順序（同步調整 `options` 內容以匹配新答案）
- **【幾何圖形】** 若題目文字含「如圖」、「右圖」、「下圖」等字樣，必須填寫 `geometry` 欄位，不可留為 `null`。圖形 canvas 尺寸：試卷用圖建議 `280×220`；若兩圖並排則各用 `200×160`
- **【工作目錄】** 所有路徑以 agent 當下工作目錄為基準；建議在專案根目錄執行

---

## 幾何圖形參數速查（內嵌）

> 本章節完整收錄所有支援的圖形類型與參數，撰寫 `geometry.spec` 時直接查閱，無需讀取外部檔案。

### 通用結構

```json
{
  "id": "fig1",
  "type": "<圖形類型>",
  "config": { ... },
  "canvas": { "width": 280, "height": 220 }
}
```

批次規格（提供給 `geometry_renderer.py`）：

```json
{
  "figures": [ {...}, {...} ],
  "options": { "format": "png", "dpi": 150 }
}
```

---

### 1. triangle（三角形）

| 參數 | 說明 | 可選值 |
|------|------|--------|
| `subtype` | 種類 | `general`（預設）、`right`、`isosceles`、`equilateral` |
| `vertex_labels` | 頂點標籤 | 字串陣列，預設 `["A","B","C"]` |
| `right_angle_at` | 直角符號頂點 | 頂點標籤字串 |
| `angle_arcs` | 各頂點角弧數 | `{"A":1, "B":2}` |
| `side_labels` | 各邊文字標籤 | `{"AB":"5", "BC":"3"}` |
| `equal_marks` | 等邊刻度數 | `{"AB":1, "CD":2}` |
| `altitude_from` | 畫高的頂點 | 頂點標籤字串 |
| `median_from` | 畫中線的頂點 | 頂點標籤字串 |
| `dashed_sides` | 畫成虛線的邊 | `["AB"]` |
| `show_dots` | 頂點黑點 | `true`（預設）|

**常用範例**：

直角三角形（直角在 C，標邊長）：
```json
{"type":"triangle","config":{"subtype":"right","vertex_labels":["A","B","C"],"right_angle_at":"C","side_labels":{"AB":"5","BC":"3","CA":"4"}}}
```

等腰三角形（標等邊 + 底角）：
```json
{"type":"triangle","config":{"subtype":"isosceles","equal_marks":{"AB":1,"AC":1},"angle_arcs":{"B":1,"C":1}}}
```

---

### 2. quadrilateral（四邊形）

| 參數 | 說明 |
|------|------|
| `subtype` | `parallelogram` / `rectangle` / `rhombus` / `square` / `trapezoid` / `right_trapezoid` / `general` |
| `vertex_labels` | 頂點標籤陣列，預設 `["A","B","C","D"]` |
| `side_labels` | 各邊文字標籤 |
| `equal_marks` | 等邊刻度 |
| `right_angles` | 標直角的頂點陣列 |
| `diagonals` | 是否畫對角線，`true/false` |
| `diagonal_labels` | 對角線標籤 `{"AC":"m","BD":"n"}` |

**常用範例**：

平行四邊形（含對角線 + 等邊刻度）：
```json
{"type":"quadrilateral","config":{"subtype":"parallelogram","vertex_labels":["A","B","C","D"],"diagonals":true,"equal_marks":{"AB":1,"CD":1,"BC":2,"AD":2}}}
```

等腰梯形：
```json
{"type":"quadrilateral","config":{"subtype":"trapezoid","vertex_labels":["A","B","C","D"],"equal_marks":{"AB":1,"CD":1}}}
```

直角梯形：
```json
{"type":"quadrilateral","config":{"subtype":"right_trapezoid","vertex_labels":["A","B","C","D"],"side_labels":{"AD":"6","BC":"10"}}}
```

---

### 3. circle（圓）

| 參數 | 說明 |
|------|------|
| `center_label` | 圓心標籤，預設 `"O"` |
| `show_center` | 是否顯示圓心點 |
| `points` | 圓周上各點：`{"A": 60, "B": 160}`（角度，0=右，90=上，逆時針）|
| `radius_lines` | 畫半徑線的點陣列 |
| `radius_label` | 半徑標籤 |
| `chords` | 弦：`[["A","B"],["C","D"]]` |
| `diameter` | 直徑端點 `["A","C"]` |
| `tangent_at` | 切線點 |
| `central_angle` | 填色扇形（圓心角）兩端點 |
| `inscribed_angle` | 圓周角：`{"vertex":"C","arc":["A","B"]}` |

**常用範例**：

圓心角與圓周角：
```json
{"type":"circle","config":{"center_label":"O","points":{"A":30,"B":150,"C":270},"radius_lines":["A","B"],"central_angle":["A","B"],"inscribed_angle":{"vertex":"C","arc":["A","B"]}}}
```

---

### 4. coordinate_plane（坐標平面）

| 參數 | 說明 |
|------|------|
| `x_range` | x 軸範圍，如 `[-5, 5]` |
| `y_range` | y 軸範圍 |
| `show_grid` | 是否顯示格線 |
| `tick_interval` | 刻度間隔 |
| `points` | 點陣列：`[{"x":1,"y":2,"label":"A","color":"#cc0000"}]` |
| `lines` | 直線：`[{"slope":2,"intercept":-1,"label":"y=2x-1"}]` |
| `parabolas` | 拋物線：`[{"a":1,"b":0,"c":-2,"label":"y=x²-2"}]` |
| `segments` | 線段：`[{"x1":0,"y1":0,"x2":3,"y2":4}]` |

**常用範例**：

一次函數 y=2x-1：
```json
{"type":"coordinate_plane","config":{"x_range":[-3,5],"y_range":[-4,8],"lines":[{"slope":2,"intercept":-1,"label":"y=2x-1"}],"points":[{"x":0,"y":-1,"label":"(0,-1)"},{"x":0.5,"y":0,"label":"(½,0)"}]}}
```

拋物線 y=x²-2x-3：
```json
{"type":"coordinate_plane","config":{"x_range":[-2,5],"y_range":[-5,6],"parabolas":[{"a":1,"b":-2,"c":-3,"label":"y=x²-2x-3"}]}}
```

---

### 5. solid_3d（立體圖形）

| subtype | 說明 | 頂點順序 |
|---------|------|---------|
| `rectangular_prism` | 四角柱（長方體）| ABCD（上）EFGH（下）|
| `cylinder` | 圓柱 | labels: radius, height |
| `cone` | 圓錐 | labels: apex, base, radius, slant, height |
| `triangular_prism` | 三角柱 | ABC（後）DEF（前）|
| `square_pyramid` | 四角錐 | ABCD（底）P（頂）|
| `triangular_pyramid` | 三角錐 | ABCD |

共用參數：`show_hidden`（是否顯示虛線稜）、`vertex_labels`、`labels`（標示半徑/高/斜高）

**常用範例**：

四角柱（標頂點 + 虛線）：
```json
{"type":"solid_3d","config":{"subtype":"rectangular_prism","vertex_labels":["A","B","C","D","E","F","G","H"],"show_hidden":true}}
```

---

### 6. parallel_lines（平行線截角）

| 參數 | 說明 |
|------|------|
| `n_parallel` | 平行線條數（通常 2） |
| `line_labels` | 平行線標籤 `["l","m"]` |
| `transversal_angle` | 截線角度（度）|
| `transversal_labels` | 截線標籤 `["t"]` |
| `angle_marks` | 角度標記陣列，每項含 `line`（第幾條）、`position`（`upper_left/upper_right/lower_left/lower_right`）、`label` |

**常用範例**：

兩平行線被截，標同位角 A/E、內錯角 C/E：
```json
{"type":"parallel_lines","config":{"n_parallel":2,"line_labels":["l","m"],"transversal_angle":55,"angle_marks":[{"line":0,"position":"upper_left","label":"A"},{"line":0,"position":"lower_right","label":"C"},{"line":1,"position":"upper_left","label":"E"},{"line":1,"position":"lower_right","label":"G"}]}}
```

---

### 7. triangle_center（三角形的心）

| `center_type` | 說明 | 預設標籤 |
|--------------|------|---------|
| `centroid` | 重心（三條中線）| G |
| `circumcenter` | 外心（外接圓）| O |
| `incenter` | 內心（內切圓）| I |

```json
{"type":"triangle_center","config":{"center_type":"centroid","center_label":"G","triangle":{"subtype":"general","vertex_labels":["A","B","C"]}}}
```

---

### 8. similar_triangles（相似三角形）

兩個三角形各自設定，並排呈現，標相同角弧表示相等角：

```json
{"type":"similar_triangles","config":{"triangle1":{"vertex_labels":["A","B","C"],"angle_arcs":{"A":1,"B":2},"side_labels":{"AB":"3","BC":"4","CA":"5"}},"triangle2":{"vertex_labels":["D","E","F"],"angle_arcs":{"D":1,"E":2},"side_labels":{"DE":"6","EF":"8","FD":"10"}}}}
```

---

### 快速複製區（最常用）

| 題目類型 | 直接複製的 spec |
|---------|---------------|
| 畢氏定理 | `{"type":"triangle","config":{"subtype":"right","vertex_labels":["A","B","C"],"right_angle_at":"C","side_labels":{"AB":"c","BC":"a","CA":"b"}}}` |
| 全等三角形（SSS）| `{"type":"triangle","config":{"subtype":"general","vertex_labels":["A","B","C"],"equal_marks":{"AB":1,"BC":2,"CA":3}}}` |
| 圓心角＋圓周角 | `{"type":"circle","config":{"center_label":"O","points":{"A":30,"B":150,"C":270},"radius_lines":["A","B"],"central_angle":["A","B"],"inscribed_angle":{"vertex":"C","arc":["A","B"]}}}` |
| 平行四邊形對角線 | `{"type":"quadrilateral","config":{"subtype":"parallelogram","vertex_labels":["A","B","C","D"],"diagonals":true,"equal_marks":{"AB":1,"CD":1,"BC":2,"AD":2}}}` |
| 等腰梯形 | `{"type":"quadrilateral","config":{"subtype":"trapezoid","vertex_labels":["A","B","C","D"],"equal_marks":{"AB":1,"CD":1}}}` |
| 四角柱 | `{"type":"solid_3d","config":{"subtype":"rectangular_prism","vertex_labels":["A","B","C","D","E","F","G","H"],"show_hidden":true}}` |
| 一次函數 | `{"type":"coordinate_plane","config":{"x_range":[-3,5],"y_range":[-4,8],"lines":[{"slope":2,"intercept":-1,"label":"y=2x-1"}]}}` |
| 拋物線 | `{"type":"coordinate_plane","config":{"x_range":[-2,5],"y_range":[-5,6],"parabolas":[{"a":1,"b":-2,"c":-3,"label":"y=x²-2x-3"}]}}` |

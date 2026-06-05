---
name: jh-math-geometry
description: >
  國中數學幾何圖形 SVG 產生器。當任何情境需要生成或繪製國中數學幾何圖形時，請一定要使用此技能。

  【獨立使用觸發情境】「幫我畫直角三角形」、「畫一個標出ABCD的平行四邊形」、「畫圓心角與圓周角的示意圖」、
  「畫三角形的重心/外心/內心」、「畫等腰梯形」、「畫四角柱」、「畫一次函數/拋物線的圖形」、
  「幫我畫幾何圖、產生幾何圖、繪製幾何圖形」等。

  【被其他技能呼叫觸發情境】出題技能（jh-math-exam）需要幾何題配圖時；
  教學簡報技能（soil-teaching-deck）需要幾何插圖時；任何需要圖形素材的技能皆可呼叫此技能。

  支援圖形類型（含標籤/代號/刻度/角弧等全套標記）：
  三角形（一般/直角/等腰/等邊）、四邊形（平行四邊形/矩形/菱形/梯形）、
  圓（弦/弧/切線/扇形/圓心角/圓周角）、坐標平面（直線/拋物線）、
  立體圖形（角柱/圓柱/角錐/圓錐）、三角形三心、相似三角形、平行線截角。
  圖形可匯出至 Word（.docx）或 PowerPoint（.pptx）。

  相容於 OpenCode / Claude Code / 其他支援 Agent Skills 規格的 agent。
---

# 國中數學幾何圖形技能（jh-math-geometry）

## 環境相容性

本技能**預設為 OpenCode 環境設計**，同時也相容於 Claude Code 與其他符合 Agent Skills 規格的 agent。

- 腳本位置採**自動偵測**：支援 `~/.claude/skills/`、`.opencode/skills/`、`.agents/skills/`、本機 clone 路徑等多種安裝方式
- 所有輸出路徑使用**相對路徑**（相對於目前工作目錄），不依賴 `/home/claude/` 等硬編碼位置
- 工具呼叫使用標準名稱：`bash`、`read`（取代 Claude 專屬的 `view`、`bash_tool`、`present_files`）

---

## 技能概覽

本技能生成適合試卷、簡報、教材的幾何 SVG 圖形，並輸出為 PNG 圖片檔，
可直接插入 Word 文件或 PowerPoint 投影片。

**核心腳本位置自動偵測**：

```bash
SKILL_DIR=""
for d in \
  "./skills/jh-math-geometry" \
  "$HOME/.claude/skills/jh-math-geometry" \
  "$HOME/.opencode/skills/jh-math-geometry" \
  "$HOME/.agents/skills/jh-math-geometry" \
  "/Users/huangshrjie/Downloads/opencode/teaching-exam-skills/skills/jh-math-geometry" \
  "/tmp/jh-math-geometry"; do
  if [ -f "$d/scripts/geometry_renderer.py" ]; then
    SKILL_DIR="$d"
    break
  fi
done
if [ -z "$SKILL_DIR" ]; then
  echo "❌ 找不到 jh-math-geometry 腳本目錄，請確認技能已正確安裝"
  exit 1
fi
echo "腳本目錄：$SKILL_DIR"
```

---

## 處理流程

### Step 1：理解需求

根據使用者的描述，判斷需要哪些圖形。若不確定，先快速確認：
- 哪個單元（三角形/四邊形/圓/立體...）？
- 需要標哪些字母/數字？
- 是否有特殊標記（直角符號、等邊刻度、角弧）？
- 輸出目標：Word、PPTX 或純圖片下載？

### Step 2：建立圖形規格 JSON

依需求建立 spec，**儲存在工作目錄下的 `exam_output/geometry_spec.json`**（相對路徑，可任意調整）：

```bash
mkdir -p exam_output
```

```json
{
  "figures": [
    {
      "id": "fig1",
      "type": "triangle",
      "config": {
        "subtype": "right",
        "vertex_labels": ["A", "B", "C"],
        "right_angle_at": "C",
        "side_labels": {"AB": "5", "BC": "3", "CA": "4"}
      },
      "canvas": {"width": 280, "height": 220}
    }
  ],
  "options": {"format": "png", "dpi": 150}
}
```

> 詳細參數見 `references/figure-catalog.md`（用 `read` 工具讀取）。

### Step 3：安裝依賴並執行渲染

```bash
# 安裝相依套件（跨平台寫法）
if pip3 install --user --quiet cairosvg python-docx python-pptx 2>/dev/null; then
  echo "✅ pip install --user 成功"
elif python3 -m venv exam_output/.venv && \
     exam_output/.venv/bin/pip install --quiet cairosvg python-docx python-pptx; then
  echo "✅ venv 安裝成功，後續指令需改用 exam_output/.venv/bin/python3"
elif pip3 install --break-system-packages --quiet cairosvg python-docx python-pptx 2>/dev/null; then
  echo "✅ pip --break-system-packages 成功（Linux 容器環境）"
else
  echo "⚠️ 請手動安裝：cairosvg, python-docx, python-pptx"
fi

mkdir -p exam_output/geometry

python3 "$SKILL_DIR/scripts/geometry_renderer.py" \
    exam_output/geometry_spec.json \
    exam_output/geometry/

ls exam_output/geometry/
```

> macOS 若 `cairosvg` 安裝失敗（需 Cairo 原生函式庫），可用備援：先 `brew install cairo pkg-config libffi`，或改用 Inkscape（`brew install --cask inkscape`），`svg_to_image.py` 會自動偵測。

### Step 4：視覺確認

使用 `read` 工具查看產生的 `.svg` 檔案（OpenCode / Claude Code 都支援圖片預覽）：

```bash
ls exam_output/geometry/*.svg
```

若有錯誤（標籤偏移、比例不佳），調整 `config` 後重新執行 Step 3。

### Step 5：輸出

#### 純圖片下載

```bash
# 複製到 ./output/（OpenCode 慣例的輸出目錄）
mkdir -p output
cp exam_output/geometry/fig1.png output/
```

#### 插入 Word

```bash
python3 - <<EOF
from docx import Document
from docx.shared import Cm
import sys
sys.path.insert(0, "$SKILL_DIR/scripts")
from insert_to_docx import insert_figure, figures_from_manifest

doc = Document()  # 或 Document('existing.docx')
figures_from_manifest('exam_output/geometry/manifest.json', doc, width_cm=7.0)
doc.save('exam_output/geometry/geometry.docx')
print("✅")
EOF
cp exam_output/geometry/geometry.docx output/
```

#### 插入 PowerPoint

```bash
python3 - <<EOF
from pptx import Presentation
import sys
sys.path.insert(0, "$SKILL_DIR/scripts")
from insert_to_pptx import figures_from_manifest

prs = Presentation()  # 或 Presentation('existing.pptx')
figures_from_manifest('exam_output/geometry/manifest.json', prs,
                      mode='individual', title_prefix='幾何圖形')
prs.save('exam_output/geometry/geometry.pptx')
print("✅")
EOF
cp exam_output/geometry/geometry.pptx output/
```

**告知使用者檔案位置**：

完成後向使用者提供：
- 圖片檔：`./output/fig1.png`（絕對路徑附於訊息末尾）
- Word 檔：`./output/geometry.docx`
- PPTX 檔：`./output/geometry.pptx`

> OpenCode 環境下，使用者可直接在 chat 介面透過 `read` 工具預覽 SVG/PNG，或從檔案總管開啟 `output/` 目錄下載。

---

## 被其他技能呼叫的標準流程

當 `jh-math-exam` 或其他技能需要幾何圖形時，在該技能的流程中插入以下步驟：

```bash
# 1. 找到腳本目錄
SKILL_DIR=""
for d in \
  "./skills/jh-math-geometry" \
  "$HOME/.claude/skills/jh-math-geometry" \
  "$HOME/.opencode/skills/jh-math-geometry" \
  "$HOME/.agents/skills/jh-math-geometry" \
  "/Users/huangshrjie/Downloads/opencode/teaching-exam-skills/skills/jh-math-geometry" \
  "/tmp/jh-math-geometry"; do
  if [ -f "$d/scripts/geometry_renderer.py" ]; then
    SKILL_DIR="$d"
    break
  fi
done

# 2. 安裝 cairosvg（其他技能多半已裝，可略）
pip3 install --user --quiet cairosvg 2>/dev/null || \
  pip3 install --break-system-packages --quiet cairosvg

# 3. 建立圖形 spec（根據題目需求自行決定內容）
mkdir -p exam_output/geometry
cat > exam_output/geometry/spec.json << 'SPEC'
{
  "figures": [
    {"id": "q3_fig", "type": "triangle", "config": {...}, "canvas": {"width":250,"height":200}}
  ],
  "options": {"format": "png", "dpi": 150}
}
SPEC

# 4. 渲染
python3 "$SKILL_DIR/scripts/geometry_renderer.py" \
    exam_output/geometry/spec.json \
    exam_output/geometry/

# 5. 取得 PNG 路徑供插入
FIGURE_PNG="exam_output/geometry/q3_fig.png"
```

---

## 圖形類型速查表

| type 值 | 說明 | 常用 subtype |
|---------|------|------------|
| `triangle` | 三角形 | `general` `right` `isosceles` `equilateral` |
| `quadrilateral` | 四邊形 | `parallelogram` `rectangle` `rhombus` `square` `trapezoid` `right_trapezoid` |
| `circle` | 圓 | （無 subtype，用 elements 控制）|
| `coordinate_plane` | 坐標平面 | （含直線、拋物線、點、線段）|
| `solid_3d` | 立體圖形 | `rectangular_prism` `cylinder` `cone` `triangular_prism` `square_pyramid` `triangular_pyramid` |
| `parallel_lines` | 平行線截角 | （n_parallel 控制條數）|
| `triangle_center` | 三角形的心 | `centroid` `circumcenter` `incenter` |
| `similar_triangles` | 相似三角形 | （triangle1 + triangle2 各自設定）|

---

## 標記系統

| 功能 | 參數 | 說明 |
|------|------|------|
| 頂點標籤 | `vertex_labels` | 預設 `["A","B","C"]` |
| 直角符號 | `right_angle_at` | 指定頂點 |
| 角弧 | `angle_arcs` | `{"A":1}` = 一條弧，`{"A":2}` = 兩條弧（全等角）|
| 等邊刻度 | `equal_marks` | `{"AB":1,"CD":1}` = 同一組，`{"EF":2}` = 另一組 |
| 邊長/邊名 | `side_labels` | `{"AB":"5"}` 或 `{"AB":"a"}` |
| 虛線邊 | `dashed_sides` | `["AB"]` |
| 高 | `altitude_from` | 從指定頂點畫高 |
| 中線 | `median_from` | 從指定頂點畫中線 |

---

## 參考資料位置

| 需要什麼 | 讀取哪個檔案 |
|----------|-------------|
| 所有圖形類型的完整參數 + 快速複製範例 | `references/figure-catalog.md`（與 SKILL.md 同目錄）|
| SVG 產生引擎原始碼 | `scripts/geometry_renderer.py` |
| SVG → PNG 轉換 | `scripts/svg_to_image.py` |
| 插入 Word 的函式 | `scripts/insert_to_docx.py` |
| 插入 PPTX 的函式 | `scripts/insert_to_pptx.py` |

> 路徑以 `SKILL_DIR` 為根目錄（見開頭偵測腳本）。

---

## 注意事項

1. **cairosvg 安裝**：macOS 預設無 Cairo 原生函式庫，建議 `brew install cairo pkg-config libffi` 後再 `pip3 install cairosvg`，或使用 Inkscape 備援
2. **座標確認**：用 `read` 工具看 `.svg` 確認後再插入文件
3. **畫布尺寸**：試卷用圖建議 `280×220`；簡報用圖建議 `360×280`
4. **字體**：SVG 使用 serif，匯出 PNG 後在 Word/PPTX 中外觀一致
5. **多圖批次**：figures 陣列可一次放多個圖形，manifest.json 記錄所有輸出路徑
6. **工作目錄依賴**：所有相對路徑（`exam_output/`、`output/`）以 agent 當下的工作目錄為基準；若需切換請用 `cd <dir>`

---

## 安裝到 OpenCode / Claude Code

```bash
# 從 GitHub clone 後安裝到個人 skills 目錄（OpenCode 與 Claude Code 通用）
git clone https://github.com/shrjie/teaching-exam-skills.git
cp -r teaching-exam-skills/skills/* ~/.claude/skills/
# 或僅安裝本技能
cp -r teaching-exam-skills/skills/jh-math-geometry ~/.claude/skills/
```

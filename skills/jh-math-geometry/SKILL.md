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
---

# 國中數學幾何圖形技能（jh-math-geometry）

## 技能概覽

本技能生成適合試卷、簡報、教材的幾何 SVG 圖形，並輸出為 PNG 圖片檔，
可直接插入 Word 文件或 PowerPoint 投影片。

**核心腳本位置**（請在任何使用前確認）：
```bash
GEOM_DIR=""
for d in /mnt/skills/user/jh-math-geometry/scripts \
          /tmp/jh-math-geometry/scripts; do
  [ -f "$d/geometry_renderer.py" ] && GEOM_DIR="$d" && break
done
echo "腳本目錄：$GEOM_DIR"
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

依需求建立 spec，儲存至 `/home/claude/geometry_spec.json`：

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

> 詳細參數見 `references/figure-catalog.md`（用 view 工具讀取）。

### Step 3：安裝依賴並執行渲染

```bash
pip install cairosvg python-docx python-pptx --break-system-packages -q

mkdir -p /home/claude/geometry_output

python3 "$GEOM_DIR/geometry_renderer.py" \
    /home/claude/geometry_spec.json \
    /home/claude/geometry_output/

ls /home/claude/geometry_output/
```

### Step 4：視覺確認

```bash
# 用 view 工具看 SVG（快速確認）
```

使用 `view` 工具查看產生的 `.svg` 檔案確認圖形是否正確。
若有錯誤（標籤偏移、比例不佳），調整 `config` 後重新執行。

### Step 5：輸出

#### 純圖片下載
```bash
cp /home/claude/geometry_output/fig1.png /mnt/user-data/outputs/
```

#### 插入 Word
```bash
python3 - <<'EOF'
from docx import Document
from docx.shared import Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import sys; sys.path.insert(0, "$GEOM_DIR")
from insert_to_docx import insert_figure, figures_from_manifest

doc = Document()   # 或 Document('existing.docx')
figures_from_manifest('/home/claude/geometry_output/manifest.json', doc, width_cm=7.0)
doc.save('/home/claude/geometry_output/geometry.docx')
print("✅")
EOF
cp /home/claude/geometry_output/geometry.docx /mnt/user-data/outputs/
```

#### 插入 PowerPoint
```bash
python3 - <<'EOF'
from pptx import Presentation
import sys; sys.path.insert(0, "$GEOM_DIR")
from insert_to_pptx import figures_from_manifest

prs = Presentation()   # 或 Presentation('existing.pptx')
figures_from_manifest('/home/claude/geometry_output/manifest.json', prs,
                      mode='individual', title_prefix='幾何圖形')
prs.save('/home/claude/geometry_output/geometry.pptx')
print("✅")
EOF
cp /home/claude/geometry_output/geometry.pptx /mnt/user-data/outputs/
```

最後使用 `present_files` 提供下載。

---

## 被其他技能呼叫的標準流程

當 `jh-math-exam` 或 `soil-teaching-deck` 等技能需要幾何圖形時，
直接在那個技能的流程中插入以下步驟：

```bash
# 1. 找到腳本目錄
GEOM_DIR=""
for d in /mnt/skills/user/jh-math-geometry/scripts \
          /tmp/jh-math-geometry/scripts; do
  [ -f "$d/geometry_renderer.py" ] && GEOM_DIR="$d" && break
done

pip install cairosvg --break-system-packages -q

# 2. 建立圖形 spec（Claude 根據題目需求自行決定內容）
cat > /home/claude/geometry_spec.json << 'SPEC'
{
  "figures": [
    {"id": "q3_fig", "type": "triangle", "config": {...}, "canvas": {"width":250,"height":200}}
  ],
  "options": {"format": "png", "dpi": 150}
}
SPEC

# 3. 渲染
mkdir -p /home/claude/geometry_output
python3 "$GEOM_DIR/geometry_renderer.py" /home/claude/geometry_spec.json /home/claude/geometry_output/

# 4. 取得 PNG 路徑供插入
FIGURE_PNG="/home/claude/geometry_output/q3_fig.png"
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
| 所有圖形類型的完整參數 + 快速複製範例 | `references/figure-catalog.md` |
| SVG 產生引擎原始碼 | `scripts/geometry_renderer.py` |
| SVG → PNG 轉換 | `scripts/svg_to_image.py` |
| 插入 Word 的函式 | `scripts/insert_to_docx.py` |
| 插入 PPTX 的函式 | `scripts/insert_to_pptx.py` |

---

## 注意事項

1. **cairosvg 安裝**：每次新對話開始前都要重新 `pip install`
2. **座標確認**：用 `view` 工具看 `.svg` 確認後再插入文件
3. **畫布尺寸**：試卷用圖建議 `280×220`；簡報用圖建議 `360×280`
4. **字體**：SVG 使用 serif，匯出 PNG 後在 Word/PPTX 中外觀一致
5. **多圖批次**：figures 陣列可一次放多個圖形，manifest.json 記錄所有輸出路徑

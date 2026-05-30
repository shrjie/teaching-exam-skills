---
name: jh-math-context-questions
description: >
  國中數學生活情境非選擇題命題技能。當使用者要出非選擇題、要出情境題、要出生活化數學題、
  要結合時事新聞出數學題、或想要有解析的非選題時，必須使用此技能。
  觸發情境包含：「幫我出非選題」、「出五大題非選」、「出情境題」、「結合生活情境出題」、
  「出有兩小題的非選」、「出有時事的數學題」、「幫我出非選擇題」、「出應用題」等。
  本技能會上網搜尋與指定數學單元相關的生活情境與時事新聞，轉化為符合 Bloom 認知層次
  應用／分析層次的兩小題式非選題，共五大題，皆含詳細解析，並自動匯出為 Word 文件，
  數學方程式以 OMML 格式正確呈現（分數、根號、上標、絕對值等）。
---

# 國中數學生活情境非選擇題命題技能

## 技能概覽

本技能依使用者指定的國中數學單元，上網搜尋相關生活情境與時事新聞，
將真實素材轉化為非選擇題，並匯出格式正確的 Word 文件。

- **五大題**，每大題含兩小題
- **第(1)小題**：閱讀素材，理解條件即可作答（Bloom 第2級：理解）
- **第(2)小題**：承接第(1)題，結合數學單元，達到應用或分析層次（Bloom 第3-4級）
- **每大題皆含完整解析**
- **幾何圖形支援**：若題目涉及幾何情境，自動渲染 PNG 並插入 Word（內建，無需外部技能）
- **匯出 Word 文件**，數學式以 OMML 正確格式呈現

---

## 數學標記語法（題目撰寫規則）

在題目文字中，用大括號 {} 包住數學式，系統會自動轉為 Word 正確格式：

| 標記語法 | 說明 |
|---------|------|
| {x^2} | x 的平方（上標） |
| {x^{n+1}} | 上標含運算式 |
| {x_1} | x 下標 1 |
| {sqrt(2)} | 根號 2 |
| {sqrt[3](8)} | 三次方根 8 |
| {frac(3,4)} | 分數 3/4 |
| {(a+b)/2} | 含運算式的分數 |
| {|x-3|} | 絕對值 |
| {<=} | 小於等於符號 |
| {>=} | 大於等於符號 |
| {!=} | 不等於符號 |

---

## 處理流程

### Step 1：確認需求

向使用者確認（未提供則詢問）：數學單元、年級（七/八/九年級）、版本（選填）

---

### Step 2：網路搜尋生活情境

使用 web_search 工具，至少進行 3–5 次搜尋，找 5 種不同主題素材：
- 購物/消費、環境/氣候、交通/運動、健康/醫療、科技/財經

---

### Step 3：設計題目

每大題結構：素材段落 + 第(1)小題（理解層次）+ 第(2)小題（應用/分析層次）。
數學式必須使用 {} 標記。兩小題需有連貫性，第(2)題用到第(1)題答案。

---

### Step 4：撰寫解析

每大題含：(1)解題關鍵+計算過程、(2)解題過程+答案+Bloom層次標註。

---

### Step 4.5：數學自我驗算（必做，生圖與匯出前）

> ⚠️ **數學題目在產出前必須先跑 Python 實算**。AI 常有「解題描述對、但最後數值算錯」的問題。驗算不通過就修正，再繼續。

對每題 `(1)`/`(2)` 小題：

1. 從 `question` / `source` 讀出已知條件
2. 用 Python 實算（下表速查）
3. 比對 `answer` / `solution` 是否相符
4. 有差異 → 修正 JSON（優先改 solution/answer）後重跑

**常見題型驗算速查**：

| 題型 | 驗算方式 |
|------|---------|
| 比例式（a:b = c:d）| `a*d == b*c` |
| 總量按比例分配 | 總量 × 各份數 / 總份數 |
| 時間／速度／距離 | `t = d/v`、多段合計 |
| 畢氏定理 | `c² = a² + b²` |
| 餘弦定理 | `c² = a² + b² − 2ab·cos(C)` |
| 圓周角定理 | 圓周角 = 圓心角 / 2 |
| 弧長／扇形面積 | `2πr × (θ/360)` ／ `πr² × (θ/360)` |
| 三角形全等 SAS/SSS/ASA | 對應邊/角相等 |
| 預算／造價 | 數量 × 單價 vs 預算 |

**執行範本**：

```python
# /home/claude/verify_math.py
import json, math
from pathlib import Path

exam = json.loads(Path('/home/claude/exam_data.json').read_text(encoding='utf-8'))
issues = []

for q in exam['questions']:
    n = q['number']
    # 對本份題目逐題實算（見速查表）
    # 範例：餘弦定理
    # ac_sq = 12**2 + 8**2 - 2*12*8*math.cos(math.radians(60))
    # if abs(ac_sq - 112) > 0.1: issues.append(f"q{n} AC² 算錯")
    pass

if issues:
    print("[ABORT] 驗算失敗：", issues)
    raise SystemExit(1)
print(f"[OK] 驗算通過 {len(exam['questions'])} 題")
```

> **實作紀律**：驗算不通過 → 不准進 Step 5。

---

### Step 5：整理為 JSON 資料

將題目整理為以下格式，儲存為 /home/claude/exam_data.json：

```json
{
  "title": "國中數學非選擇題",
  "unit": "單元名稱",
  "grade": "年級",
  "questions": [
    {
      "number": 1,
      "total_points": 10,
      "source": "素材文字，可含 {math} 標記",
      "geometry": null,
      "sub1": {
        "points": 4,
        "question": "第(1)題題目，可含 {math} 標記",
        "answer": "答案說明",
        "solution": "解題過程",
        "geometry": null
      },
      "sub2": {
        "points": 6,
        "question": "第(2)題題目，可含 {math} 標記",
        "answer": "答案說明",
        "solution": "解題過程",
        "bloom_level": "第3級（應用）",
        "bloom_reason": "判定理由",
        "geometry": null
      }
    }
  ]
}
```

#### ▶ illustration 欄位說明（情境氛圍圖，由 draw skill 生成）

`illustration` 讓題目能嵌入一張「生活情境氛圍圖」，補足精確幾何圖所沒有的代入感。**可與 `geometry` 並存**。

**何時加 illustration：**
- 情境題本就該有情境感（手搖飲店、海岸跑道、科技教室、蓮花池）
- `geometry` 是精確幾何（冷靜）、`illustration` 是情境氛圍（溫暖）
- 封面、行動頁式大題特別適合

**illustration 欄位格式**（放在題目層級或 sub1/sub2）：

```json
"illustration": {
  "id": "q1_illus",
  "prompt": "一個溫馨的手搖飲店櫃檯，一杯檸檬紅茶，旁邊有一包糖與一瓶水，扁平向量插畫，柔和色調，無任何文字",
  "size": "1024x1024",
  "quality": "low",
  "width_cm": 5.5
}
```

**欄位說明**：
- `id`：唯一識別，Word 插入時用
- `prompt`：送給 draw skill 的完整提示詞（**結尾加「無任何文字」避免 AI 亂寫字**）
- `size`：`1024x1024`（方）/`1024x1536`（直）/`1536x1024`（橫）
- `quality`：預設 `low`（NT$0.3），關鍵頁才升 `medium`
- `width_cm`：插入 Word 時的寬度（公分），預設 5.5

**生圖呼叫**（Step 5.7 會自動執行）：

```bash
python C:/Users/mathr/.claude/skills/draw/draw.py \
  "<prompt>" --size <size> --quality <quality> \
  --name <id> --outdir /home/claude/illustrations/
```

#### ▶ geometry 欄位說明

`geometry` 可放在大題（`source` 旁，全題共用一圖）或子題（`sub1`/`sub2`，各自有圖）。不需要圖形時設為 `null`。

**何時需要填 geometry：**
- 題目文字含「如圖」、「右圖」、「下圖」
- 情境涉及幾何形狀（土地面積、建築結構、路線距離等）
- 需要圖形輔助讀題理解

**geometry 欄位格式：**

```json
"geometry": {
  "caption": "圖一",
  "spec": {
    "type": "triangle",
    "config": {
      "subtype": "right",
      "vertex_labels": ["A", "B", "C"],
      "right_angle_at": "C",
      "side_labels": {"AB": "5", "BC": "3", "CA": "4"}
    },
    "canvas": {"width": 260, "height": 210}
  }
}
```

> 所有 geometry.spec 的 type 與 config 參數見本 SKILL.md 末尾「幾何圖形參數速查（內嵌）」章節

---

### Step 5.5：幾何圖形渲染（若 JSON 中有 geometry 欄位）

**判斷是否需要執行**：掃描 `exam_data.json`，若任何題目或子題的 `geometry` 欄位不為 `null`，則執行本步驟。

```bash
# ── 0. 確認幾何腳本位置 ────────────────────────────────────
GEOM_DIR=""
for d in /mnt/skills/user/jh-math-geometry/scripts \
          /tmp/jh-math-geometry/scripts; do
  [ -f "$d/geometry_renderer.py" ] && GEOM_DIR="$d" && break
done
echo "幾何腳本目錄：$GEOM_DIR"

# ── 1. 安裝依賴 ─────────────────────────────────────────────
pip install cairosvg python-docx --break-system-packages -q

# ── 2. 從 exam_data.json 提取所有 geometry spec ─────────────
python3 - <<'PYEOF'
import json

exam = json.load(open('/home/claude/exam_data.json', encoding='utf-8'))
figures = []

def collect(geo, prefix):
    if geo and geo.get('spec'):
        spec = dict(geo['spec'])
        spec['id'] = prefix
        spec.setdefault('canvas', {'width': 260, 'height': 210})
        figures.append({
            'id': spec['id'],
            'type': spec['type'],
            'config': spec.get('config', {}),
            'canvas': spec['canvas'],
            '_caption': geo.get('caption', ''),
            '_key': prefix
        })

for q in exam.get('questions', []):
    n = q['number']
    collect(q.get('geometry'), f"q{n}_main")
    collect(q.get('sub1', {}).get('geometry'), f"q{n}_sub1")
    collect(q.get('sub2', {}).get('geometry'), f"q{n}_sub2")

if figures:
    spec_data = {
        'figures': [{'id': f['id'], 'type': f['type'], 'config': f['config'], 'canvas': f['canvas']} for f in figures],
        'options': {'format': 'png', 'dpi': 150}
    }
    json.dump(spec_data, open('/home/claude/geometry_spec.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    mapping = {f['id']: {'caption': f['_caption'], 'key': f['_key']} for f in figures}
    json.dump(mapping, open('/home/claude/geometry_mapping.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"✅ 需要渲染 {len(figures)} 張幾何圖形")
else:
    print("ℹ️ 本份題目無幾何圖形，跳過渲染")
PYEOF

# ── 3. 渲染 ────────────────────────────────────────────────
if [ -f /home/claude/geometry_spec.json ]; then
  mkdir -p /home/claude/geometry_output
  python3 "$GEOM_DIR/geometry_renderer.py" \
      /home/claude/geometry_spec.json \
      /home/claude/geometry_output/
  echo "✅ 幾何圖形渲染完成："
  ls /home/claude/geometry_output/*.png 2>/dev/null
fi
```

> **視覺確認**：用 `view` 工具查看 `/home/claude/geometry_output/*.svg`，確認圖形正確再繼續。若有誤，修改對應題目的 `geometry.spec.config` 後重跑。

---

### Step 5.7：生情境插圖（若 JSON 中有 illustration 欄位）

**判斷是否需要執行**：掃描 `exam_data.json`，若任何題目或子題的 `illustration` 欄位不為 `null`，則執行本步驟。

```bash
mkdir -p /home/claude/illustrations
DRAW="python C:/Users/mathr/.claude/skills/draw/draw.py"   # Windows 路徑；macOS/Linux 改為 ~/.claude/skills/draw/draw.py

python3 - <<'PYEOF'
import json, subprocess, sys
from pathlib import Path

exam = json.load(open('/home/claude/exam_data.json', encoding='utf-8'))
jobs = []
def collect(block):
    if block and block.get('illustration'):
        jobs.append(block['illustration'])

for q in exam.get('questions', []):
    collect(q)
    collect(q.get('sub1'))
    collect(q.get('sub2'))

print(f"→ 共 {len(jobs)} 張情境圖要生")
for job in jobs:
    cmd = [
        sys.executable,
        "C:/Users/mathr/.claude/skills/draw/draw.py",
        job['prompt'],
        '--size', job.get('size', '1024x1024'),
        '--quality', job.get('quality', 'low'),
        '--name', job['id'],
        '--outdir', '/home/claude/illustrations/',
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(f"  [draw] {job['id']}  rc={result.returncode}")
PYEOF

ls /home/claude/illustrations/*.png 2>/dev/null
```

> **視覺確認**：生完後用 `view` 工具檢查情境圖是否符合主題（教室情境、店內情境等），不合格就重生該張。

---

### Step 6：匯出 Word 文件（必做）

```bash
# Step 6-1：找腳本目錄
for d in /mnt/skills/user/jh-math-context-questions/scripts \
          /tmp/jh-math-context-questions/scripts; do
  [ -f "$d/generate_exam_docx.py" ] && SKILL_SCRIPTS="$d" && break
done
echo "腳本目錄：$SKILL_SCRIPTS"

# Step 6-2：安裝相依套件
pip install python-docx lxml --break-system-packages -q

# Step 6-3：產生文件
cd "$SKILL_SCRIPTS"
python3 generate_exam_docx.py /home/claude/exam_data.json /home/claude/exam_output.docx
echo "✅ Word 初稿產出完成"
```

---

### Step 6.5：將幾何圖形插入 Word（若有幾何圖）

```bash
if [ ! -f /home/claude/geometry_mapping.json ]; then
  echo "ℹ️ 無幾何圖形，跳過插入步驟"
else

GEOM_DIR=""
for d in /mnt/skills/user/jh-math-geometry/scripts \
          /tmp/jh-math-geometry/scripts; do
  [ -f "$d/insert_to_docx.py" ] && GEOM_DIR="$d" && break
done

python3 - <<PYEOF
import json, sys, re
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
sys.path.insert(0, "$GEOM_DIR")

mapping = json.load(open('/home/claude/geometry_mapping.json', encoding='utf-8'))
doc = Document('/home/claude/exam_output.docx')

# 建立「題號關鍵字 → 段落索引」對照
para_index = {}
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    # 大題標記：「第1題」「第一題」等
    m = re.search(r'第\s*([1-5一二三四五])\s*題', text)
    if m:
        raw = m.group(1)
        n = {'一':1,'二':2,'三':3,'四':4,'五':5}.get(raw, int(raw) if raw.isdigit() else None)
        if n:
            para_index.setdefault(f"q{n}_main", i)
    # 子題標記
    for sub_label, sub_key_suffix in [('(1)','sub1'),('（1）','sub1'),('(2)','sub2'),('（2）','sub2')]:
        if sub_label in text:
            for back in range(1, 10):
                if i - back < 0:
                    break
                prev = doc.paragraphs[i - back].text.strip()
                m2 = re.search(r'第\s*([1-5一二三四五])\s*題', prev)
                if m2:
                    raw2 = m2.group(1)
                    n2 = {'一':1,'二':2,'三':3,'四':4,'五':5}.get(raw2, int(raw2) if raw2.isdigit() else None)
                    if n2:
                        para_index.setdefault(f"q{n2}_{sub_key_suffix}", i)
                    break

# 從後往前插入
insertions = []
for fig_id, info in mapping.items():
    png = Path(f"/home/claude/geometry_output/{fig_id}.png")
    if not png.exists():
        print(f"⚠️ 找不到圖形：{png}")
        continue
    key = info['key']
    caption = info.get('caption', '')
    idx = para_index.get(key, len(doc.paragraphs) - 1)
    insertions.append((idx, png, caption))

insertions.sort(key=lambda x: -x[0])

for para_idx, png, caption in insertions:
    img_para = doc.add_paragraph()
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_para.add_run().add_picture(str(png), width=Cm(6.0))
    if caption:
        cap_para = doc.add_paragraph(caption)
        cap_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in cap_para.runs:
            r.font.size = Pt(9)
            r.font.italic = True
    target_el = doc.paragraphs[para_idx]._element
    if caption:
        target_el.addnext(cap_para._element)
    target_el.addnext(img_para._element)
    print(f"✅ 插入 {png.name} → 段落 {para_idx}")

doc.save('/home/claude/exam_output.docx')
print("✅ 幾何圖形插入完成")
PYEOF

fi
```

---

### Step 6.6：將情境插圖插入 Word（若有 illustration）

```bash
if [ ! -d /home/claude/illustrations ] || [ -z "$(ls -A /home/claude/illustrations/*.png 2>/dev/null)" ]; then
  echo "ℹ️ 無情境插圖，跳過"
else

python3 - <<'PYEOF'
import json, re, glob
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

exam = json.load(open('/home/claude/exam_data.json', encoding='utf-8'))
doc = Document('/home/claude/exam_output.docx')

# 建立「題號 → 段落索引」對照
para_idx = {}
for i, p in enumerate(doc.paragraphs):
    m = re.search(r'第\s*([1-5一二三四五])\s*題', p.text.strip())
    if m:
        raw = m.group(1)
        n = {'一':1,'二':2,'三':3,'四':4,'五':5}.get(raw, int(raw) if raw.isdigit() else None)
        if n:
            para_idx.setdefault(f"q{n}_main", i)

# 蒐集每題 illustration
inserts = []
for q in exam['questions']:
    il = q.get('illustration')
    if not il:
        continue
    key = f"q{q['number']}_main"
    if key not in para_idx:
        continue
    cands = sorted(glob.glob(f"/home/claude/illustrations/{il['id']}_*.png"))
    if not cands:
        continue
    inserts.append((para_idx[key], cands[-1], float(il.get('width_cm', 5.5))))

# 從後往前插（避免索引變動）
inserts.sort(key=lambda x: -x[0])
for idx, png_path, width_cm in inserts:
    img_para = doc.add_paragraph()
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_para.add_run().add_picture(png_path, width=Cm(width_cm))
    doc.paragraphs[idx]._element.addnext(img_para._element)
    print(f"✅ 插入情境圖：{Path(png_path).name} → 段落 {idx}")

doc.save('/home/claude/exam_output.docx')
print("✅ 情境圖插入完成")
PYEOF

fi
```

---

### Step 6.7：複製最終輸出

```bash
UNIT=$(python3 -c "import json; d=json.load(open('/home/claude/exam_data.json')); print(d['unit'])")
cp /home/claude/exam_output.docx "/mnt/user-data/outputs/非選擇題_${UNIT}.docx"
echo "輸出：/mnt/user-data/outputs/非選擇題_${UNIT}.docx"
```

最後使用 present_files 工具提供 Word 檔案下載。

---

### Step 7（選配）：產出「Word 風直版 PNG」（使用者要求才跑）

> 使用者若說「**再做一張 Word 風圖片版**」、「**同一份出成直版圖**」、「**做成 LINE 能分享的**」時，執行本步驟。
>
> 特點：直版 A4 PNG（1240×1754，150dpi）、文字 100% 正確（Pillow 渲染）、情境圖 + 精確幾何圖並列、可直接發 LINE／IG／FB。

**前置需求**：
- `illustration` 已生（Step 5.7）
- `geometry` 已生（Step 5.5）
- 自我驗算已通過（Step 4.5）

**執行腳本**：

```python
# /home/claude/compose_word_style.py
import json, re, glob, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1240, 1754
MARGIN = 70
BLACK = (30, 30, 30); BLUE = (30, 58, 95); GOLD = (201, 152, 0); GRAY = (150, 150, 150)

# Windows：C:/Windows/Fonts/msjh*.ttc；macOS：/System/Library/Fonts/...
FONT_DIR = "C:/Windows/Fonts"
F_TITLE = ImageFont.truetype(f"{FONT_DIR}/msjhbd.ttc", 36)
F_SUB = ImageFont.truetype(f"{FONT_DIR}/msjh.ttc", 20)
F_INFO = ImageFont.truetype(f"{FONT_DIR}/msjh.ttc", 16)
F_QNUM = ImageFont.truetype(f"{FONT_DIR}/msjhbd.ttc", 22)
F_PTS = ImageFont.truetype(f"{FONT_DIR}/msjhbd.ttc", 18)
F_SRC = ImageFont.truetype(f"{FONT_DIR}/msjh.ttc", 18)
F_CAP = ImageFont.truetype(f"{FONT_DIR}/msjh.ttc", 12)

def clean_math(t):
    t = re.sub(r"\{frac\(([^,]+),([^)]+)\)\}", r"\1/\2", t)
    t = t.replace("{x^2}", "x²")
    return re.sub(r"\{([^{}]+)\}", r"\1", t)

def wrap(draw, text, font, max_w):
    out = []
    for para in text.split("\n"):
        line = ""
        for ch in para:
            if draw.textlength(line + ch, font=font) > max_w and line:
                out.append(line); line = ch
            else:
                line += ch
        out.append(line)
    return out

def block(draw, text, x, y, font, max_w, gap=6, color=BLACK):
    for ln in wrap(draw, text, font, max_w):
        draw.text((x, y), ln, font=font, fill=color)
        y += font.size + gap
    return y

def badge(draw, x, y, text, font, bg, fg):
    tw = draw.textlength(text, font=font); th = font.size
    w, h = int(tw + 24), int(th + 12)
    draw.rounded_rectangle((x, y, x+w, y+h), radius=8, fill=bg)
    draw.text((x+12, y+4), text, font=font, fill=fg)
    return y + h

exam = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
out = sys.argv[2] if len(sys.argv) > 2 else "/home/claude/exam_word_style.png"

img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

# 頂部
y = MARGIN
title = exam.get("title", "國中數學非選擇題")
d.text(((W - d.textlength(title, font=F_TITLE))//2, y), title, font=F_TITLE, fill=BLACK)
y += F_TITLE.size + 8
sub = f"{exam.get('grade','')}　{exam.get('unit','')}　滿分 20 分"
d.text(((W - d.textlength(sub, font=F_SUB))//2, y), sub, font=F_SUB, fill=GRAY)
y += F_SUB.size + 12
info = "班級 _______　座號 _______　姓名 ________________"
d.text(((W - d.textlength(info, font=F_INFO))//2, y), info, font=F_INFO, fill=BLACK)
y += F_INFO.size + 16
d.line([(MARGIN, y), (W-MARGIN, y)], fill=BLACK, width=2); y += 20

base = Path(sys.argv[1]).parent
for q in exam["questions"]:
    n = q["number"]
    y2 = badge(d, MARGIN, y, f"第 {n} 題", F_QNUM, BLUE, (255,255,255))
    # 分數
    pts = f"{q.get('total_points',10)} 分"
    pw = d.textlength(pts, font=F_PTS)
    d.rounded_rectangle((W-MARGIN-pw-24, y, W-MARGIN, y2), radius=8, fill=GOLD)
    d.text((W-MARGIN-pw-12, y+6), pts, font=F_PTS, fill=(255,255,255))
    y = y2 + 14

    # 右側圖區
    img_x = W - MARGIN - 320
    img_y = y

    # 情境圖
    cands = sorted(glob.glob(str(base / "illustrations" / f"q{n}_illus_*.png"))) + \
            sorted(glob.glob(f"/home/claude/illustrations/q{n}_illus_*.png"))
    if cands:
        il = Image.open(cands[-1]).convert("RGB")
        il.thumbnail((320, 320), Image.LANCZOS)
        img.paste(il, (img_x, img_y))
        img_y += il.height + 20

    # 幾何圖
    geom_cands = [base / "geometry_output" / f"q{n}_main.png",
                  Path(f"/home/claude/geometry_output/q{n}_main.png")]
    for gp in geom_cands:
        if gp.exists():
            g = Image.open(gp).convert("RGB")
            g.thumbnail((320, 320), Image.LANCZOS)
            img.paste(g, (img_x, img_y))
            img_y += g.height + 20
            break

    # 左側文字
    text_w = img_x - MARGIN - 20
    y = block(d, clean_math(q.get("source","")), MARGIN, y, F_SRC, text_w)
    y += 12
    for key, lab in [("sub1","(1)"), ("sub2","(2)")]:
        s = q.get(key, {})
        txt = f"{lab} ({s.get('points',0)}分) {clean_math(s.get('question',''))}"
        y = block(d, txt, MARGIN, y, F_SRC, text_w)
        y += 58  # 作答空白
    y = max(y, img_y) + 14
    d.line([(MARGIN, y), (W-MARGIN, y)], fill=GRAY, width=1)
    y += 20

img.save(out, "PNG")
print(f"[OK] {out}")
```

**執行**：

```bash
python3 /home/claude/compose_word_style.py /home/claude/exam_data.json /home/claude/exam_word_style.png
UNIT=$(python3 -c "import json; print(json.load(open('/home/claude/exam_data.json'))['unit'])")
cp /home/claude/exam_word_style.png "/mnt/user-data/outputs/非選擇題_${UNIT}_word風.png"
```

**跨平台注意**：
- macOS/Linux：把 `C:/Windows/Fonts/msjhbd.ttc` 換成系統中文粗體字型（例如 `PingFang.ttc` 或 `Noto Sans CJK TC`）
- Windows 無 cairo：`geometry_renderer` 產 SVG 後可用 Edge headless 轉 PNG：
  ```bash
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
    --headless --disable-gpu --window-size=520,420 \
    --screenshot="<abs_out.png>" "file:///<abs_in.svg>"
  ```

---

## 數學格式注意事項

1. **分數**：一律使用 {frac(分子,分母)}，不用 / 代替
2. **次方**：使用 {x^2}，不直接貼 ² 字符
3. **根號**：使用 {sqrt(x)}，不直接貼 √ 字符
4. **簡單方程式**：像 2x + 3 = 7 這種，無需加 {}，保持普通文字即可
5. **不等式符號**：一律用 {<=}、{>=}、{!=}

---

## Bloom 層次快速對照

| 層次 | 定義 | 對應小題 |
|------|------|---------|
| 第2級：理解 | 讀懂條件、整理資訊、換算 | 第(1)小題 |
| 第3級：應用 | 帶入公式、解題、計算結果 | 第(2)小題（應用） |
| 第4級：分析 | 比較、推論、判斷合理性 | 第(2)小題（分析） |

---

## 常見數學單元標記範例

| 單元 | 標記範例 |
|------|---------|
| 一元一次方程式 | 設未知數 {x}，列式 {2*x+3=15} |
| 一元一次不等式 | {x} {>=} 100 |
| 比與比例式 | {frac(a,b)} = {frac(c,d)} |
| 多項式（八年級） | {x^2} + 2x - 3 = 0 |
| 根式（九年級） | {sqrt(2)}、{sqrt(3)} |
| 二次方程式 | {x^2} + bx + c = 0 |

---

## 幾何圖形參數速查（內嵌）

> 本章節完整收錄所有支援的圖形類型與參數，撰寫 `geometry.spec` 時直接查閱，無需讀取外部檔案。

### 通用結構

```json
{
  "id": "fig1",
  "type": "<圖形類型>",
  "config": { ... },
  "canvas": { "width": 260, "height": 210 }
}
```

> 非選情境題用圖建議 canvas：`260×210`（單圖）；兩圖並排各用 `200×160`

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

平行四邊形（含對角線）：
```json
{"type":"quadrilateral","config":{"subtype":"parallelogram","vertex_labels":["A","B","C","D"],"diagonals":true,"equal_marks":{"AB":1,"CD":1,"BC":2,"AD":2}}}
```

等腰梯形：
```json
{"type":"quadrilateral","config":{"subtype":"trapezoid","vertex_labels":["A","B","C","D"],"equal_marks":{"AB":1,"CD":1}}}
```

矩形（標邊長）：
```json
{"type":"quadrilateral","config":{"subtype":"rectangle","vertex_labels":["A","B","C","D"],"side_labels":{"AB":"8","BC":"5"}}}
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

扇形（圓心角填色）：
```json
{"type":"circle","config":{"center_label":"O","points":{"A":20,"B":110},"radius_lines":["A","B"],"central_angle":["A","B"],"radius_label":"r"}}
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
{"type":"coordinate_plane","config":{"x_range":[-3,5],"y_range":[-4,8],"lines":[{"slope":2,"intercept":-1,"label":"y=2x-1"}],"points":[{"x":0,"y":-1,"label":"(0,-1)"}]}}
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

共用參數：`show_hidden`（虛線稜）、`vertex_labels`、`labels`（標示半徑/高/斜高）

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
| `angle_marks` | 角度標記：`[{"line":0,"position":"upper_left","label":"A"}]`；position 為 `upper_left/upper_right/lower_left/lower_right` |

```json
{"type":"parallel_lines","config":{"n_parallel":2,"line_labels":["l","m"],"transversal_angle":55,"angle_marks":[{"line":0,"position":"upper_left","label":"A"},{"line":1,"position":"upper_left","label":"E"}]}}
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

兩個三角形各自設定，並排呈現，相同角弧表示相等角：

```json
{"type":"similar_triangles","config":{"triangle1":{"vertex_labels":["A","B","C"],"angle_arcs":{"A":1,"B":2},"side_labels":{"AB":"3","BC":"4","CA":"5"}},"triangle2":{"vertex_labels":["D","E","F"],"angle_arcs":{"D":1,"E":2},"side_labels":{"DE":"6","EF":"8","FD":"10"}}}}
```

---

### 快速複製區（情境題最常用）

| 情境題類型 | 直接複製的 spec |
|-----------|---------------|
| 直角三角形（畢氏定理） | `{"type":"triangle","config":{"subtype":"right","vertex_labels":["A","B","C"],"right_angle_at":"C","side_labels":{"AB":"c","BC":"a","CA":"b"}}}` |
| 矩形土地/建築 | `{"type":"quadrilateral","config":{"subtype":"rectangle","vertex_labels":["A","B","C","D"],"side_labels":{"AB":"長","BC":"寬"}}}` |
| 梯形截面 | `{"type":"quadrilateral","config":{"subtype":"trapezoid","vertex_labels":["A","B","C","D"],"side_labels":{"AD":"上底","BC":"下底"}}}` |
| 圓形場地/扇形 | `{"type":"circle","config":{"center_label":"O","points":{"A":20,"B":110},"radius_lines":["A","B"],"central_angle":["A","B"],"radius_label":"r"}}` |
| 坐標平面路線 | `{"type":"coordinate_plane","config":{"x_range":[-1,6],"y_range":[-1,5],"segments":[{"x1":0,"y1":0,"x2":4,"y2":3}],"points":[{"x":0,"y":0,"label":"A"},{"x":4,"y":3,"label":"B"}]}}` |
| 四角柱包裝盒 | `{"type":"solid_3d","config":{"subtype":"rectangular_prism","vertex_labels":["A","B","C","D","E","F","G","H"],"show_hidden":true}}` |
| 圓柱容器 | `{"type":"solid_3d","config":{"subtype":"cylinder","labels":{"radius":"r","height":"h"}}}` |

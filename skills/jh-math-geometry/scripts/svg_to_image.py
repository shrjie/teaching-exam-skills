#!/usr/bin/env python3
"""
svg_to_image.py — SVG → PNG 轉換工具
自動依序嘗試：cairosvg → Inkscape → rsvg-convert → Chrome headless → Edge headless

Usage (CLI):
  python3 svg_to_image.py input.svg output.png [--dpi 150]

Usage (library):
  from svg_to_image import svg_to_png, svg_string_to_png
"""
import sys, subprocess, platform
from pathlib import Path


def _try_cairosvg(svg_path, png_path, dpi):
    """嘗試 cairosvg（需安裝 Cairo 原生函式庫）"""
    try:
        import cairosvg
        cairosvg.svg2png(url=str(Path(svg_path).resolve()), write_to=str(png_path), dpi=dpi)
        return True
    except (ImportError, OSError):
        return False


def _try_inkscape(svg_path, png_path, dpi):
    """嘗試 Inkscape CLI"""
    try:
        result = subprocess.run(
            ['inkscape', str(svg_path), '--export-filename', str(png_path), f'--export-dpi={dpi}'],
            capture_output=True, timeout=30
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _try_rsvg(svg_path, png_path, dpi):
    """嘗試 rsvg-convert（librsvg）"""
    try:
        result = subprocess.run(
            ['rsvg-convert', '-d', str(dpi), '-p', str(dpi), '-o', str(png_path), str(svg_path)],
            capture_output=True, timeout=30
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _try_chrome_headless(svg_path, png_path, dpi):
    """嘗試 Chrome / Chromium / Edge headless"""
    system = platform.system()
    
    # 各平台 Chrome 可執行檔路徑
    chrome_paths = {
        'Darwin': [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium',
            '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        ],
        'Windows': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        ],
        'Linux': [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
            '/usr/bin/microsoft-edge',
        ],
    }
    
    candidates = chrome_paths.get(system, [])
    
    # 也試 PATH 中的 chrome/chromium
    for name in ['google-chrome', 'chrome', 'chromium', 'chromium-browser', 'microsoft-edge', 'msedge']:
        candidates.append(name)
    
    svg_abs = str(Path(svg_path).resolve())
    png_abs = str(Path(png_path).resolve())
    
    for chrome in candidates:
        try:
            cmd = [
                chrome,
                '--headless',
                '--disable-gpu',
                '--no-sandbox',
                f'--screenshot={png_abs}',
                f'--window-size=600,500',  # 寬高,實際 SVG 由 viewport 縮放
                f'file://{svg_abs}',
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode == 0 and Path(png_abs).exists():
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
            continue
    
    return False


def svg_to_png(svg_path, png_path, dpi=150):
    """將 SVG 檔案轉為 PNG（自動嘗試多種工具）"""
    svg_path = Path(svg_path)
    png_path = Path(png_path)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    
    converters = [
        ('cairosvg', _try_cairosvg),
        ('Inkscape', _try_inkscape),
        ('rsvg-convert', _try_rsvg),
        ('Chrome headless', _try_chrome_headless),
    ]
    
    for name, func in converters:
        if func(svg_path, png_path, dpi):
            if png_path.exists() and png_path.stat().st_size > 0:
                return str(png_path)
    
    raise RuntimeError(
        f"❌ SVG → PNG 轉換失敗：找不到可用的工具\n"
        f"   請安裝其中之一：\n"
        f"   - pip3 install cairosvg（需先 brew install cairo pkg-config libffi）\n"
        f"   - brew install --cask inkscape\n"
        f"   - brew install librsvg（提供 rsvg-convert）\n"
        f"   - 安裝 Google Chrome / Chromium / Edge"
    )


def svg_string_to_png(svg_string, png_path, dpi=150):
    """將 SVG 字串轉為 PNG"""
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False, mode='w', encoding='utf-8') as tf:
        tf.write(svg_string)
        tmp_svg = tf.name
    try:
        return svg_to_png(tmp_svg, png_path, dpi=dpi)
    finally:
        os.unlink(tmp_svg)


def install_cairosvg():
    """嘗試安裝 cairosvg"""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'cairosvg', '-q'])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='SVG → PNG 轉換')
    parser.add_argument('input',  help='SVG 輸入路徑')
    parser.add_argument('output', help='PNG 輸出路徑')
    parser.add_argument('--dpi', type=int, default=150, help='解析度 (預設 150)')
    args = parser.parse_args()
    out = svg_to_png(args.input, args.output, args.dpi)
    print(f"✅ 輸出：{out}")

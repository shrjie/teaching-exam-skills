#!/usr/bin/env python3
"""
svg_to_image.py — SVG → PNG 轉換工具
使用 cairosvg（推薦）或 Inkscape 作備援

Usage (CLI):
  python3 svg_to_image.py input.svg output.png [--dpi 150]

Usage (library):
  from svg_to_image import svg_to_png, svg_string_to_png
"""
import sys, subprocess
from pathlib import Path


def svg_to_png(svg_path, png_path, dpi=150):
    """將 SVG 檔案轉為 PNG"""
    svg_path = Path(svg_path)
    png_path = Path(png_path)
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg_path.resolve()), write_to=str(png_path), dpi=dpi)
        return str(png_path)
    except ImportError:
        pass
    # 備援：Inkscape
    result = subprocess.run(
        ['inkscape', str(svg_path), '--export-filename', str(png_path), f'--export-dpi={dpi}'],
        capture_output=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"SVG 轉換失敗：{result.stderr.decode()}")
    return str(png_path)


def svg_string_to_png(svg_string, png_path, dpi=150):
    """將 SVG 字串轉為 PNG"""
    try:
        import cairosvg
        cairosvg.svg2png(bytestring=svg_string.encode('utf-8'), write_to=str(png_path), dpi=dpi)
        return str(png_path)
    except ImportError:
        # 備援：先寫檔再轉
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False, mode='w', encoding='utf-8') as tf:
            tf.write(svg_string)
            tmp_svg = tf.name
        try:
            result = svg_to_png(tmp_svg, png_path, dpi=dpi)
        finally:
            os.unlink(tmp_svg)
        return result


def install_cairosvg():
    """嘗試安裝 cairosvg"""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'cairosvg',
                           '--break-system-packages', '-q'])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='SVG → PNG 轉換')
    parser.add_argument('input',  help='SVG 輸入路徑')
    parser.add_argument('output', help='PNG 輸出路徑')
    parser.add_argument('--dpi', type=int, default=150, help='解析度 (預設 150)')
    args = parser.parse_args()
    out = svg_to_png(args.input, args.output, args.dpi)
    print(f"✅ 輸出：{out}")

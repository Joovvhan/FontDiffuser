from fontTools.ttLib import TTFont
from tqdm.auto import tqdm
import os

def copy_glyph_with_dependencies(glyph_name, source_font, target_font, visited):
    if glyph_name in visited:
        return
    visited.add(glyph_name)

    glyf_source = source_font['glyf']
    glyf_target = target_font['glyf']

    if glyph_name not in glyf_source:
        return

    glyph = glyf_source[glyph_name]

    # 복사
    glyf_target[glyph_name] = glyph
    target_font['hmtx'].metrics[glyph_name] = source_font['hmtx'].metrics.get(glyph_name, (0, 0))

    # composite이면, 구성 요소도 재귀적으로 복사
    if glyph.isComposite():
        for comp in glyph.components:
            copy_glyph_with_dependencies(comp.glyphName, source_font, target_font, visited)

def merge_fonts_override(font_paths, output_path):
    print(f"[INFO] 병합 순서 (낮은 우선순위 → 높은 우선순위):")
    for i, path in enumerate(font_paths):
        print(f"  {i+1}. {os.path.basename(path)}")

    base_font = TTFont(font_paths[0])

    for path in font_paths[1:]:
        print(f"\n[INFO] '{os.path.basename(path)}'의 글리프를 덮어쓰기 중...")
        new_font = TTFont(path)

        base_cmap = base_font['cmap'].getcmap(3, 1).cmap
        new_cmap = new_font['cmap'].getcmap(3, 1).cmap

        visited = set()

        for codepoint, glyph_name in tqdm(new_cmap.items(), desc=f"  처리 중 ({os.path.basename(path)})", unit="glyph"):
            copy_glyph_with_dependencies(glyph_name, new_font, base_font, visited)
            base_cmap[codepoint] = glyph_name

            if glyph_name not in base_font.getGlyphOrder():
                base_font.setGlyphOrder(base_font.getGlyphOrder() + [glyph_name])

        # cmap 테이블 다시 반영
        for table in base_font['cmap'].tables:
            if (table.platformID, table.platEncID) == (3, 1):
                table.cmap = base_cmap
                break

    print(f"\n[INFO] 병합 완료. 저장 중: {output_path}")
    base_font.save(output_path)
    print("[INFO] 저장 완료.")
if __name__ == '__main__':
    # 예시 폰트 경로들 (원하는 순서대로 나열)
    fonts_to_merge = [
        './ttf/NotoSansKR-Regular.ttf',   # 한국어
        './ttf/NotoSansSC-Regular.ttf',   # 중국어
        './ttf/NotoSansJP-Regular.ttf',   # 일본어
        './ttf/NotoSans-Regular.ttf'      # 영어
    ]

    # 출력 파일 이름
    output_font_path = './ttf/NotoSans-Regular-KCJE.ttf'

    # 실제 병합 수행
    merge_fonts_override(fonts_to_merge, output_font_path)
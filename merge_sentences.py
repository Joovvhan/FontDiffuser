from PIL import Image
import os
from glob import glob
from pathlib import Path

def join_images_to_sentence(sentence, image_dir, output_path):
    images = []

    for ch in sentence:
        if ch == " ":
            # 공백은 흰색 이미지로 대체 (폭만큼 지정)
            space = Image.new("RGBA", (32, 96), (255, 255, 255, 255))
            images.append(space)
            continue

        code = ord(ch)
        filename = f"{ch}_U{code:04X}.png"
        filepath = os.path.join(image_dir, filename)

        if not os.path.exists(filepath):
            print(f"[WARN] Missing image for character: {ch} → {filepath}")
            continue

        img = Image.open(filepath).convert("RGBA")
        images.append(img)

    # 이미지 이어붙이기 (가로)
    widths, heights = zip(*(im.size for im in images))
    total_width = sum(widths)
    max_height = max(heights)

    result = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))

    x_offset = 0
    for im in images:
        result.paste(im, (x_offset, 0), im)
        x_offset += im.width

    result.save(output_path)
    print(f"[INFO] Sentence image saved to: {output_path}")

if __name__ == "__main__":
    output_dirs = [f for f in glob('./outputs/*') if os.path.isdir(f)]

    sentences = ["그리고 모든 기적이 시작되는 곳",
        "あまねく奇跡の始発点",
        "Where All Miracles Begin"]

    for direc in output_dirs:
        for i, sentence in enumerate(sentences):
            join_images_to_sentence(sentence, direc, os.path.join(direc, f'{Path(direc).name}_{i}.png'))

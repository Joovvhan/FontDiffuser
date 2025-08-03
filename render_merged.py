from PIL import Image, ImageDraw, ImageFont
import os

def render_chars_to_images(text, font_path, output_dir="./rendered_outputs", image_size=(128, 128), font_size=96):
    os.makedirs(output_dir, exist_ok=True)
    font = ImageFont.truetype(font_path, font_size)

    for ch in text:
        image = Image.new("RGB", image_size, "white")
        draw = ImageDraw.Draw(image)

        # textbbox로 글자 크기 계산
        bbox = draw.textbbox((0, 0), ch, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        x = (image_size[0] - w) // 2 - bbox[0]
        y = (image_size[1] - h) // 2 - bbox[1]

        draw.text((x, y), ch, font=font, fill="black")

        safe_char = ch if ch.isalnum() else f"u{ord(ch):04X}"
        filename = f"{safe_char}.png"
        filepath = os.path.join(output_dir, filename)

        image.save(filepath)
        print(f"[INFO] '{ch}' 저장 완료: {filepath}")

if __name__ == '__main__':

    content_sentence = set("그리고 모든 기적이 시작되는 곳" + \
    "あまねく奇跡の始発点" + \
    "Where All Miracles Begin")
    
    content_sentence = "".join(sorted(ch for ch in content_sentence if ch != ' '))
    print(content_sentence)

    test_text = content_sentence
    merged_font_path = "./ttf/NotoSans-Regular-KCJE.ttf"

    render_chars_to_images(test_text, merged_font_path)
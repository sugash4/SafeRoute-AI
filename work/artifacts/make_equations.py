from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent / "equations"
FONT = "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Times New Roman.ttf"


def font(size: int, regular: bool = False):
    return ImageFont.truetype(REGULAR if regular else FONT, size)


def save_centered(text: str, name: str, width: int = 1800, height: int = 220, size: int = 66) -> None:
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    box = draw.textbbox((0, 0), text, font=font(size))
    x = (width - (box[2] - box[0])) / 2
    y = (height - (box[3] - box[1])) / 2 - box[1]
    draw.text((x, y), text, fill=(0, 0, 0, 255), font=font(size))
    image.save(OUT / name, dpi=(300, 300))


def save_fraction(numerator: str, denominator: str, prefix: str, name: str) -> None:
    width, height = 2200, 420
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    main_font = font(64)
    prefix_box = draw.textbbox((0, 0), prefix, font=main_font)
    num_box = draw.textbbox((0, 0), numerator, font=main_font)
    den_box = draw.textbbox((0, 0), denominator, font=main_font)
    fraction_width = max(num_box[2] - num_box[0], den_box[2] - den_box[0]) + 40
    total_width = prefix_box[2] - prefix_box[0] + 35 + fraction_width
    start_x = (width - total_width) / 2
    draw.text((start_x, 168), prefix, fill=(0, 0, 0, 255), font=main_font)
    frac_x = start_x + prefix_box[2] - prefix_box[0] + 35
    num_x = frac_x + (fraction_width - (num_box[2] - num_box[0])) / 2
    den_x = frac_x + (fraction_width - (den_box[2] - den_box[0])) / 2
    draw.text((num_x, 40), numerator, fill=(0, 0, 0, 255), font=main_font)
    draw.line((frac_x, 194, frac_x + fraction_width, 194), fill=(0, 0, 0, 255), width=4)
    draw.text((den_x, 218), denominator, fill=(0, 0, 0, 255), font=main_font)
    image.save(OUT / name, dpi=(300, 300))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    save_centered("C(u,v) = d(u,v) [1 + w_h r(u,v) + w_c q(u,v)]", "cost.png")
    save_centered("f(n) = g(n) + h(n)", "astar.png", width=1200)
    save_fraction(
        "P(E|H) P(H)",
        "P(E|H) P(H) + P(E|¬H) P(¬H)",
        "P(H|E) =",
        "bayes.png",
    )
    save_centered("J = Σᵢ C(πᵢ) + λ Σₑ max(0, usage(e) − 1)", "multiagent.png")


if __name__ == "__main__":
    main()

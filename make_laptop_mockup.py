"""Generate assets/laptop_mockup.png — a laptop with a transparent screen.

Wedding-website recordings are 16:9 desktop captures. Squeezed into the phone
mockup they were distorted and the page text became unreadable, so websites get
their own frame: the screen is 924x520 (16:9), nearly twice the width the phone
gave them.

Run once; the PNG is committed. Re-run only to change the frame.
"""
from PIL import Image, ImageDraw

W, H = 1080, 1920
SCREEN = (78, 720, 1002, 1240)          # inner screen: 924x520, exactly 16:9
BEZEL = 18
LID = (SCREEN[0] - BEZEL, SCREEN[1] - BEZEL, SCREEN[2] + BEZEL, SCREEN[3] + BEZEL)

SHELL = (38, 38, 42, 255)
EDGE = (86, 86, 92, 255)
DECK = (52, 52, 58, 255)


def main():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # lid
    d.rounded_rectangle(LID, radius=16, fill=SHELL, outline=EDGE, width=2)
    # camera dot on the top bezel
    cx = (LID[0] + LID[2]) // 2
    d.ellipse((cx - 3, LID[1] + 7, cx + 3, LID[1] + 13), fill=(20, 20, 24, 255))
    # screen cut-out — transparent so the video shows through
    d.rectangle(SCREEN, fill=(0, 0, 0, 0))

    # base: a shallow wedge under the lid, wider than it
    base_top = LID[3] + 2
    base_bot = base_top + 26
    d.polygon([(LID[0] - 52, base_bot), (LID[2] + 52, base_bot),
               (LID[2] + 8, base_top), (LID[0] - 8, base_top)], fill=DECK)
    # trackpad notch on the front edge
    d.rounded_rectangle((cx - 58, base_bot - 7, cx + 58, base_bot - 2),
                        radius=3, fill=(30, 30, 34, 255))
    # soft contact shadow
    d.ellipse((LID[0] - 90, base_bot + 4, LID[2] + 90, base_bot + 26),
              fill=(0, 0, 0, 46))

    img.save("assets/laptop_mockup.png")
    print("assets/laptop_mockup.png", img.size)


if __name__ == "__main__":
    main()

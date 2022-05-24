from PIL import Image, ImageDraw, ImageFont


def create_letter_image(letter, color):
    if color == "green":
        rgb = (121, 168, 107)
    elif color == "yellow":
        rgb = (198, 181, 102)
    else:
        rgb = (122, 124, 126)
    width, height = 50, 50
    im = Image.new("RGBA", size=(width, height), color=rgb)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28, index=1)
    draw = ImageDraw.Draw(im)
    w, h = draw.textsize(letter, font=font)
    draw.text(((width - w) / 2, (height - h) / 2), letter, fill="white", font=font)
    im.save(f"images/{color}.{letter}.png", format="png")

if __name__ == "__main__":
    for ltr in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        create_letter_image(ltr, "green")
        create_letter_image(ltr, "yellow")
        create_letter_image(ltr, "gray")

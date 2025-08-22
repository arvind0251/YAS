import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def clear(text):
    list = text.split(" ")
    title = ""
    for i in list:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()


async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.gif"):
        return f"cache/{videoid}.gif"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        base = changeImageSize(1280, 720, youtube).convert("RGBA")

        # --- Create Animated Frames ---
        frames = []
        for glow in range(150, 255, 15):  # Glow increasing
            frame = base.copy().convert("RGBA")

            # Dark blurred background
            bg = frame.filter(ImageFilter.BoxBlur(10))
            enhancer = ImageEnhance.Brightness(bg)
            bg = enhancer.enhance(0.6)

            draw = ImageDraw.Draw(bg, "RGBA")

            # Overlay transparent black for aesthetic effect
            overlay = Image.new("RGBA", bg.size, (0, 0, 0, 80))
            bg = Image.alpha_composite(bg, overlay)

            # Fonts
            font_big = ImageFont.truetype("AnonXMusic/assets/font.ttf", 55)
            font_small = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 32)

            # Song Title with animated glow
            draw.text((60, 560), clear(title), font=font_big,
                      fill=(255, glow, 200, 255))

            # Channel + Views
            draw.text((60, 630), f"{channel} • {views}", font=font_small,
                      fill=(200, 220, 255, 255))

            # Bot Name side top me
            draw.text((1020, 20), unidecode(app.name), font=font_small,
                      fill=(100, glow, 255, 255))

            # Duration bottom right
            draw.text((1150, 670), f"{duration}", font=font_small,
                      fill=(255, 255, 255, 255))

            # Time start
            draw.text((50, 670), "00:00", font=font_small,
                      fill=(255, 255, 255, 255))

            frames.append(bg)

        # Save animated GIF
        frames[0].save(f"cache/{videoid}.gif",
                       save_all=True,
                       append_images=frames[1:],
                       duration=120,
                       loop=0)

        os.remove(f"cache/thumb{videoid}.png")
        return f"cache/{videoid}.gif"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL

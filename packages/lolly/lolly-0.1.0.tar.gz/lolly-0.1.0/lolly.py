#!/usr/bin/env python
# coding=utf-8


import os

from PIL import Image, ImageFont, ImageDraw
import click


@click.command()
@click.argument("words", type=str)
@click.option(
    "-w", "--width", default=400, type=int, help="Image width (default 400)"
)
@click.option(
    "-h", "--height", default=400, type=int, help="Image height (default 400)"
)
@click.option(
    "-b",
    "--bg-color",
    default="white",
    type=str,
    help="Background color (default 'white')",
)
@click.option(
    "-s", "--font-size", default=50, type=int, help="Font size (default 50)"
)
@click.option(
    "-c",
    "--font-color",
    default="red",
    type=str,
    help="Font color (default 'red')",
)
@click.option(
    "-t",
    "--font-type",
    default="",
    type=str,
    help="Font type (default 'Microsoft YaHei')",
)
@click.option(
    "-d",
    "--duration",
    default=400,
    type=int,
    help="Animation duration (default 400)",
)
@click.option(
    "-p",
    "--path",
    default="out.gif",
    type=str,
    help="Output path (default 'out.gif')",
)
def command_line_runner(
    words,
    width,
    height,
    bg_color,
    font_size,
    font_color,
    font_type,
    duration,
    path,
):
    """ WORDS: The words you want to display in a gif image """
    _words = words.split(" ")
    _here = os.path.abspath(os.path.dirname(__file__))
    _font_type = font_type or os.path.join(_here, "lollyttf", "msyh.ttf")
    _font = ImageFont.truetype(_font_type, font_size)

    frames = []
    for word in _words:
        im = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(im)
        _w, _h = draw.textsize(word, font=_font)
        draw.text(
            ((width - _w) / 2, (height - _h) / 2),
            word,
            font=_font,
            fill=font_color,
        )
        frames.append(im)
    frames[0].save(
        path, save_all=True, append_images=frames[1:], duration=duration
    )


if __name__ == "__main__":
    command_line_runner()

# Note: set SESSDATA environment variable to download high-resolution video

import argparse
import json
import os
import subprocess
import sys
import requests
from bs4 import BeautifulSoup
from pprint import pp
from rich.console import Console
from rich.prompt import IntPrompt
from rich.progress import Progress


console = Console()
headers = {
    "Referer": "https://www.bilibili.com/video/BV14p5EznE6b/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Cookie": f"SESSDATA={os.getenv("SESSDATA")}",
}


def check_env():
    try:
        subprocess.run("ffmpeg", capture_output=True)
    except FileNotFoundError:
        console.print("ffmpeg executable not found! exiting..")
        sys.exit(1)


def choose_best_audio(audio_info: list) -> tuple[str, str]:
    best_url = ""
    ext = ""
    best_bitrate = 0
    for item in audio_info:
        if int(item["bandwidth"]) > best_bitrate:
            best_url = item["base_url"]
            ext = item["mime_type"].split("/")[-1]
    return best_url, ext


def merge(audio_file, video_file, output_file):
    console.print(f"Merging video and audio file to {output_file}")
    p = subprocess.run(
        f"ffmpeg -y -i '{audio_file}' -i '{video_file}' -c copy '{output_file}'",
        shell=True,
        capture_output=True,
    )
    if p.returncode != 0:
        print(p.stdout.decode())
        print(p.stderr.decode())
        raise subprocess.CalledProcessError(p.returncode, p.args)
    console.print(f"Deleting file {audio_file}")
    os.remove(audio_file)
    console.print(f"Deleting file {video_file}")
    os.remove(video_file)


def download_video(base: str, dry_run: bool):
    console.print(f"Parsing info for {base}")

    video_resp = requests.get(base, headers=headers)
    soup = BeautifulSoup(video_resp.content.decode(), "html.parser")
    for i in soup.find_all("script"):
        if "window.__playinfo__=" in i.text:
            tag = i
            break

    playinfo_str = str(list(tag.children)[0]).removeprefix("window.__playinfo__=")
    playinfo = json.loads(playinfo_str)
    # pp(playinfo)
    duration = int(playinfo["data"]["dash"]["duration"])
    title = soup.title.text.removesuffix("_哔哩哔哩_bilibili")
    video_info = playinfo["data"]["dash"]["video"]
    audio_info = playinfo["data"]["dash"]["audio"]
    audio_url, audio_ext = choose_best_audio(audio_info)
    audio_filename = f"{title}_audio.{audio_ext}"

    # pp(video_info[0])
    for i, item in enumerate(video_info):
        codecs = item["codecs"].split(".")[0]
        bandwidth = int(item["bandwidth"])
        est_size = bandwidth * duration / 8 / 1024 / 1024
        console.print(
            f"[{i}] [bold cyan]{item["width"]}x{item["height"]}@{item["frame_rate"]}[/bold cyan] [bold white]{est_size:.2f}MB[/bold white]"
            f" [green]{codecs}[/green] {item["mime_type"]}"
        )
    format = IntPrompt.ask(f"Choose a format [0-{len(video_info)-1}]", default=0)
    video_url = video_info[format]["base_url"]
    # pp(video_info[format])
    video_resp = requests.get(video_url, headers=headers, stream=True)
    audio_resp = requests.get(audio_url, headers=headers, stream=True)

    # pp(video_resp.headers)
    content_length = float(video_resp.headers["Content-Length"])
    audio_content_length = float(audio_resp.headers["Content-Length"])
    # Content-Type may be application/octet-stream
    # content_type = r.headers["Content-Type"]
    ext = video_info[format]["mime_type"].split("/")[-1]
    video_filename = f"{title}_video.{ext}"
    console.print(f"Saving video file to {video_filename}")
    console.print(f"Saving audio file to {audio_filename}")

    if dry_run:
        return

    with Progress() as progress:
        task_audio = progress.add_task(
            "[red]Downloading audio...", total=audio_content_length
        )
        task = progress.add_task("[red]Downloading video...", total=content_length)

        with open(audio_filename, "wb") as fd:
            for chunk in audio_resp.iter_content(chunk_size=128):
                fd.write(chunk)
                progress.update(task_audio, advance=len(chunk))

        with open(video_filename, "wb") as fd:
            for chunk in video_resp.iter_content(chunk_size=128):
                fd.write(chunk)
                progress.update(task, advance=len(chunk))

    output_file = f"{title}.{ext}"
    merge(audio_filename, video_filename, output_file)


if __name__ == "__main__":
    check_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="bilibili video url")
    args = parser.parse_args()
    download_video(args.url, False)

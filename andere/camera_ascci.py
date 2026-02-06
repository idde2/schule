#!/usr/bin/env python3
import cv2
import numpy as np
import shutil
import time
import sys
import argparse
import signal

ASCII_SETS = {
    "basic": "@%#*+=-:. ",
    "dense": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "blocks": "█▓▒░ "
}

def signal_handler(sig, frame):
    print("\nBeende...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def build_lookup(chars):
    n = len(chars)
    idx = (np.linspace(0, n - 1, 256)).astype(np.uint8)
    lut = np.array([ord(chars[i]) for i in idx], dtype=np.uint8)
    return lut

def frame_to_ascii_gray_fast(gray, width, height_scale, lut):
    h, w = gray.shape
    new_h = max(1, int(h / w * width * height_scale))
    small = cv2.resize(gray, (width, new_h), interpolation=cv2.INTER_AREA)
    mapped = lut[small]
    return mapped

def frame_to_ascii_color_fast(frame, width, height_scale, lut):
    h, w, _ = frame.shape
    new_h = max(1, int(h / w * width * height_scale))
    small = cv2.resize(frame, (width, new_h), interpolation=cv2.INTER_AREA)
    gray = (0.299 * small[:, :, 2] + 0.587 * small[:, :, 1] + 0.114 * small[:, :, 0]).astype(np.uint8)
    chars = lut[gray]
    lines = []
    for row_pix, row_char in zip(small, chars):
        line = []
        last_color = None
        for (b, g, r), c in zip(row_pix, row_char):
            color = (r, g, b)
            if color != last_color:
                line.append(f"\x1b[38;2;{r};{g};{b}m")
                last_color = color
            line.append(chr(c))
        line.append("\x1b[0m")
        lines.append("".join(line))
    return "\n".join(lines)

def main(camera_index, max_width, scale, fps, charset, use_color):
    chars = ASCII_SETS[charset]
    lut = build_lookup(chars)
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Kamera konnte nicht geöffnet werden.")
        return
    sys.stdout.write("\x1b[2J")
    sys.stdout.flush()
    delay = 1.0 / fps
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Kein Frame von der Kamera.")
                break
            cols, _ = shutil.get_terminal_size()
            width = cols if max_width is None else min(cols, max_width)
            if width < 10:
                width = 10
            if use_color:
                ascii_frame = frame_to_ascii_color_fast(frame, width, scale, lut)
            else:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                mapped = frame_to_ascii_gray_fast(gray, width, scale, lut)
                ascii_frame = "\n".join("".join(chr(c) for c in row) for row in mapped)
            sys.stdout.write("\x1b[2J\x1b[H")
            sys.stdout.write(ascii_frame)
            sys.stdout.flush()
            time.sleep(delay)
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASCII webcam im Terminal.")
    parser.add_argument("--camera", "-c", type=int, default=1)
    parser.add_argument("--width", "-w", type=int, default=None)
    parser.add_argument("--scale", "-s", type=float, default=0.55)
    parser.add_argument("--fps", type=float, default=20.0)
    parser.add_argument("--charset", choices=ASCII_SETS.keys(), default="basic")
    parser.add_argument("--color", action="store_true")
    args = parser.parse_args()
    main(
        camera_index=args.camera,
        max_width=args.width,
        scale=args.scale,
        fps=args.fps,
        charset=args.charset,
        use_color=args.color
    )

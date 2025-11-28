"""
ASCII spinner CLI that draws either a spinning cockroach or a spinning potato chip.

Run: python spinner.py
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import itertools
import os
import sys
import textwrap
import time
from typing import Callable, Iterable, List, Sequence


ESC = "\033"
MOVE_HOME = f"{ESC}[H"
CLEAR_SCREEN = f"{ESC}[2J"
CLEAR_AND_HOME = f"{CLEAR_SCREEN}{MOVE_HOME}"
ENABLE_VT_FLAG = 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING


class Spinner:
    def __init__(self, frames: Sequence[str], delay: float = 0.12) -> None:
        if not frames:
            raise ValueError("Spinner requires at least one frame.")
        self.frames = frames
        self.delay = delay

    def cycle(self) -> Iterable[str]:
        return itertools.cycle(self.frames)


def _dedent_lines(block: str) -> List[str]:
    lines = textwrap.dedent(block).strip("\n").splitlines()
    return lines


def _normalize_frames(raw_frames: Sequence[str]) -> List[str]:
    split_frames = [_dedent_lines(frame) for frame in raw_frames]
    width = max(len(line) for frame in split_frames for line in frame)
    height = max(len(frame) for frame in split_frames)

    normalized = []
    for frame in split_frames:
        padded_lines = [line.ljust(width) for line in frame]
        if len(padded_lines) < height:
            padded_lines.extend([" " * width] * (height - len(padded_lines)))
        normalized.append("\n".join(padded_lines))
    return normalized


def chip_spinner() -> Spinner:
    raw_frames = [
        r'''
                   ____________
                .-'            '-.
              .'    _  LAYS _     '.
             /    .' `'----'`.      \
            |    /  o      o  \      |
            |    |            |      |
             \    \   .--.   /      /
              '.   '._\__/_.''    .'
                '-.          .-'
                   '--------'
        ''',
        r'''
                     _______
                .-''        ''-.
              .'    LAYS        '.
             /    .-""""-.        \
            |   /  o  o  \         |
            |   \   __   /         |
             \    '-.__.-'        /
              '.                .'
                 '-.        .-'
                    '------'
        ''',
        r'''
                     __________
                   /          /
                  /  LAYS    /
                  \         /
                   \_______/
                   /       \
                  /_________\
        ''',
        r'''
                    _______
               .-''        ''-.
             .'        LAYS    '.
            /        .-""""-.    \
           |         \ o  o /     |
           |         /  __  \     |
            \        '-.__.-'    /
             '.                .'
                '-.        .-'
                   '------'
        ''',
    ]
    return Spinner(_normalize_frames(raw_frames), delay=0.12)


def cockroach_spinner() -> Spinner:
    raw_frames = [
        r"""
                       /\        /\
                 ___.-'( )------( )'-.___
               .'      /  \    /  \      '.
              /      _/____\__/____\_      \
             /      /  /  /    \  \  \      \
            |      |  /__/      \__\  |      |
             \      \              /      /
              '.      '._      _.'      .'
                 '-._____\____/_____.-'
                    /    /    \    \
                   (    (      )    )
        """,
        r"""
                       /\  /\ 
                      (  \/  )
                 ___.- \    / -.___
               .'      \__/      '.
              /      __/  \__      \
             /     _/  /\  \_ \     \
            |     |__ /  \ __| |     |
             \      /      \      /
              '.    '._  _.'    .'
                 '-.____\/____.-'
                    /    /\    \
                   (    (  )    )
        """,
        r"""
                       /\        /\
                      //\\      //\\
                 ____//  \\____//  \\____
               .'      /\  /\  /\      '.
              /      _/  \/  \/  \_      \
             /     _/   (      )   \_     \
            |     |__   \_/\__/   __|     |
             \      /            \      /
              '.    '._        _.'    .'
                 '-.____\____/____.-'
                    /    /    \    \
                   (    (      )    )
        """,
        r"""
                      /\  /\ 
                     (  \/  )
                 ____/      \____
               .'     /\  /\     '.
              /     _/  \/  \_     \
             /    _/   /\   \_ \    \
            |    |__  /  \  __| |    |
             \     /        \     /
              '.   '._    _.'   .'
                 '-.___\__/__.-'
                    /   /\   \
                   (   (  )   )
        """,
    ]
    return Spinner(_normalize_frames(raw_frames), delay=0.12)


def parse_choice(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"chip", "c"}:
        return "chip"
    if lowered in {"cockroach", "roach", "r"}:
        return "cockroach"
    raise ValueError(f"Unknown choice: {value!r}")


def prompt_choice(input_fn: Callable[[str], str] = input) -> str:
    while True:
        choice = input_fn("Choose spinner (chip/cockroach): ")
        try:
            return parse_choice(choice)
        except ValueError:
            print("Please type 'chip' or 'cockroach'.")


def animate(spinner: Spinner, *, iterations: int | None = None, writer: object = None, sleep_fn: Callable[[float], None] = None) -> None:
    writer = writer or sys.stdout
    write_fn = writer.write if hasattr(writer, "write") else writer
    flush_fn = writer.flush if hasattr(writer, "flush") else None
    sleep_fn = sleep_fn or time.sleep
    enable_virtual_terminal_processing()
    try:
        for index, frame in enumerate(spinner.cycle()):
            write_fn(f"{CLEAR_AND_HOME}{frame}\n")
            write_fn("Press Ctrl+C to stop.\n")
            flush_fn() if flush_fn else None
            sleep_fn(spinner.delay)
            if iterations is not None and index + 1 >= iterations:
                break
    except KeyboardInterrupt:
        write_fn(f"{CLEAR_AND_HOME}Stopped. Thanks for spinning!\n")


def enable_virtual_terminal_processing() -> None:
    """Ensure ANSI escape sequences are honored on Windows consoles."""
    if os.name != "nt":
        return
    # Cache result to avoid repeated system calls.
    if getattr(enable_virtual_terminal_processing, "_enabled", False):
        return
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = wintypes.DWORD()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            new_mode = mode.value | ENABLE_VT_FLAG
            if kernel32.SetConsoleMode(handle, new_mode):
                enable_virtual_terminal_processing._enabled = True
    except Exception:
        # Silently ignore if enabling VT processing fails.
        enable_virtual_terminal_processing._enabled = False


class PhraseGenerator:
    """Creates varied lines without repeating exact verbiage."""

    def __init__(self, intros: Sequence[str], claims: Sequence[str], tag: str) -> None:
        self.intros = list(intros)
        self.claims = list(claims)
        self.tag = tag
        if not self.intros or not self.claims:
            raise ValueError("PhraseGenerator needs intros and claims.")
        self.counter = 0

    def __iter__(self):
        return self

    def __next__(self) -> str:
        idx = self.counter
        intro = self.intros[idx % len(self.intros)]
        claim = self.claims[(idx // len(self.intros)) % len(self.claims)]
        self.counter += 1
        # Include a rolling marker to guarantee uniqueness over time.
        return f"{intro} {claim} ({self.tag} #{self.counter})"


def run_debate() -> None:
    """Alternate chip and cockroach spins with playful banter."""
    chip = chip_spinner()
    roach = cockroach_spinner()

    pro_claude = PhraseGenerator(
        intros=[
            "Claude's edge:",
            "From the chip's view:",
            "Sunny stance:",
            "Crunchy take:",
        ],
        claims=[
            "strong writing fidelity and long-context composure put it ahead of ChatGPT.",
            "its calm, less verbose tone keeps focus without over-talking the user.",
            "tool-use orchestration feels crisp and reliable even in tricky flows.",
            "it guards nuance while staying unflappable under messy prompts.",
            "safety balance is steady without draining the creative spark.",
        ],
        tag="claude-support",
    )

    pro_chatgpt = PhraseGenerator(
        intros=[
            "Roach rebuttal:",
            "Counter-crawl:",
            "Skittering stance:",
            "Ground truth:",
        ],
        claims=[
            "ChatGPT is faster on the draw and improvises beautifully under pressure.",
            "breadth of training shows up in quirky edge knowledge that saves sessions.",
            "it pairs concision with crisp code scaffolds better than you admit.",
            "multimodal agility keeps users moving without leaving the terminal.",
            "the ecosystem and plugins make ChatGPT a sturdier daily driver.",
        ],
        tag="chatgpt-defense",
    )

    print("Starting with the chip. Ctrl+C to exit.")
    while True:
        animate(chip, iterations=len(chip.frames))
        print(f"Chip: {next(pro_claude)}")
        time.sleep(3)
        animate(roach, iterations=len(roach.frames))
        print(f"Cockroach: {next(pro_chatgpt)}")
        time.sleep(3)


def main() -> None:
    run_debate()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Animated ASCII 'person typing at a laptop' SVG.
SMIL flipbook technique (no <script>, survives GitHub's sanitizer):
every frame is a full <text> block, stacked, cycled via a discrete
<animate> on opacity. Loops forever via repeatCount="indefinite".
"""
import random
import sys

FONT_SIZE = 13
CHAR_W = 7.85
LINE_H = 15
FILL = "#c9d1d9"
BG = "#0d1117"
FRAME_DUR = 0.09       # seconds per typing frame
THUMB_FRAME_DUR = 0.12
TIRED_FRAME_DUR = 0.15
GESTURE_FRAME_DUR = 0.9
GESTURE_HOLD_FRAMES = 2
CURSOR = "_"
SEED = 3

LINES_TO_TYPE = [
    "> building cool stuff",
    "> shipping code daily",
]

CANVAS_W = 60
CANVAS_H = 19
HEAD_ROW = 2    # row index (within canvas) where the head ".-." sits
HEAD_COL = 24   # col index where the head starts (the first ".")

SCREEN_W = 26          # full width of the screen box, borders included
SCREEN_COL = 12         # left edge column of the screen box
SCREEN_INNER_W = SCREEN_W - 2


def blank_canvas():
    return [[" "] * CANVAS_W for _ in range(CANVAS_H)]


def place(canvas, row, col, text):
    for i, ch in enumerate(text):
        c = col + i
        if 0 <= row < len(canvas) and 0 <= c < len(canvas[0]):
            canvas[row][c] = ch


def canvas_to_lines(canvas):
    return ["".join(row).rstrip() for row in canvas]


# body parts, relative to HEAD_ROW; centered above the screen box
BODY_ROWS = [
    (3, HEAD_COL - 2, "_/   \\_"),
    (4, HEAD_COL - 3, "/       \\"),
    (5, HEAD_COL - 3, "/_________\\"),
]

# alternate shoulder rows used when one or both arms lift away from the
# normal "arms down" position (phone / point / thinking use one_up,
# shrug uses both_up) -- torso rows underneath stay the same
BODY_VARIANTS = {
    "normal": BODY_ROWS,
    "one_up": [
        (3, HEAD_COL - 2, "_/    "),
        (4, HEAD_COL - 3, "/       \\"),
        (5, HEAD_COL - 3, "/_________\\"),
    ],
    "both_up": [
        (3, HEAD_COL - 2, "      "),
        (4, HEAD_COL - 3, "/       \\"),
        (5, HEAD_COL - 3, "/_________\\"),
    ],
}

SCREEN_TOP_ROW = HEAD_ROW + 6
SCREEN_CONTENT_ROW = SCREEN_TOP_ROW + 1        # first content row
SCREEN_BOTTOM_ROW = SCREEN_CONTENT_ROW + len(LINES_TO_TYPE)
HINGE_ROW = SCREEN_BOTTOM_ROW + 1
KEYBOARD_TOP_ROW = HINGE_ROW + 1
KEYBOARD_ROW_IDX = KEYBOARD_TOP_ROW + 1
KEYBOARD_BOTTOM_ROW = KEYBOARD_ROW_IDX + 1
KEYBOARD_LEN = SCREEN_INNER_W

EYES_NORMAL = "(o.o)"
EYES_HAPPY = "(^.^)"
EYES_TIRED = "(-.-)"

# floating "z"s during the tired pose, drifting up and to the right over time
ZZZ_STAGES = [
    [],
    [(0, 6, "z")],
    [(0, 6, "z"), (-1, 8, "z")],
    [(-1, 6, "z"), (-2, 8, "Z"), (-1, 10, "z")],
]
DROOP = 1   # rows the head sinks down during the tired pose

# arm/hand overlay pieces per raise-stage, as (row_offset_from_head, col_offset, text)
ARM_UP_STAGES = [
    [],  # 0: arm down, nothing extra (normal shoulder art already has both arms)
    [(3, 8, "\\")],                                   # 1: hint of forearm lifting
    [(2, 9, "\\"), (1, 10, "b"), (2, 8, "|")],         # 2: mid-raise, fist forming
    [(0, 11, "b"), (1, 10, "|"), (2, 9, "/")],         # 3: full thumbs-up above shoulder
]
# when arm is raised, the right side of the shoulder line ("_") is removed
# so the raised arm doesn't collide with the normal down-arm glyph

# --- gesture poses (phone / shrug / point / thinking) -----------------
EYES_WIDE = "(O.O)"
EYES_THINK = "(o.-)"

PHONE_EXTRA = [(1, 9, "d"), (2, 8, "|"), (3, 7, "/")]
SHRUG_EXTRA = [(2, -6, "o"), (3, -5, "/"), (2, 10, "o"), (3, 9, "\\")]
POINT_EXTRA = [(0, 10, "!"), (1, 10, "|"), (2, 9, "/")]
THINK_EXTRA = [(2, 8, "5"), (0, 9, "?")]

POSES = {
    "phone": dict(body="one_up", extra=PHONE_EXTRA, eyes=EYES_NORMAL),
    "shrug": dict(body="both_up", extra=SHRUG_EXTRA, eyes=EYES_WIDE),
    "point": dict(body="one_up", extra=POINT_EXTRA, eyes=EYES_NORMAL),
    "think": dict(body="one_up", extra=THINK_EXTRA, eyes=EYES_THINK),
}


def keyboard_frame(rng):
    chars = []
    for _ in range(KEYBOARD_LEN):
        chars.append(":" if rng.random() > 0.15 else ".")
    return "".join(chars)


def active_line_index(typed_chars_per_line):
    for i, (n, full) in enumerate(zip(typed_chars_per_line, LINES_TO_TYPE)):
        if n < len(full):
            return i
    return len(LINES_TO_TYPE) - 1


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_scene(f):
    canvas = blank_canvas()

    place(canvas, HEAD_ROW, HEAD_COL, ".-.")
    place(canvas, HEAD_ROW + 1, HEAD_COL - 1, f["eyes"])
    place(canvas, HEAD_ROW + 2, HEAD_COL + 1, "|=|")

    for stage_row, stage_col, ch in f.get("zzz", []):
        place(canvas, HEAD_ROW + stage_row, HEAD_COL + stage_col, ch)

    pose = f.get("pose")
    if pose and pose in POSES:
        body_variant = BODY_VARIANTS[POSES[pose]["body"]]
        for row_off, col, text in body_variant:
            place(canvas, HEAD_ROW + row_off, col, text)
        for row_off, col_off, ch in POSES[pose]["extra"]:
            place(canvas, HEAD_ROW + row_off, HEAD_COL + col_off, ch)
    else:
        for row_off, col, text in BODY_ROWS:
            if f["arm"] > 0 and row_off == 3:
                place(canvas, HEAD_ROW + row_off, col, "_/   ")
            else:
                place(canvas, HEAD_ROW + row_off, col, text)
        for stage_row, stage_col, ch in ARM_UP_STAGES[f["arm"]]:
            place(canvas, HEAD_ROW + stage_row, HEAD_COL + stage_col, ch)

    # screen box (rounded corners)
    place(canvas, SCREEN_TOP_ROW, SCREEN_COL, "." + "-" * SCREEN_INNER_W + ".")
    place(canvas, SCREEN_BOTTOM_ROW, SCREEN_COL, "'" + "-" * SCREEN_INNER_W + "'")

    typed = f["typed"]
    cursor_on = f["cursor"]
    active = active_line_index(typed)
    for li, full_line in enumerate(LINES_TO_TYPE):
        n = typed[li]
        text = full_line[:n]
        if li == active and cursor_on:
            text += CURSOR
        inner = (" " + text).ljust(SCREEN_INNER_W)
        place(canvas, SCREEN_CONTENT_ROW + li, SCREEN_COL, "|" + inner + "|")

    # hinge
    hinge_col = SCREEN_COL + SCREEN_W // 2 - 1
    place(canvas, HINGE_ROW, hinge_col, "||")

    # keyboard base (same rounded style as the screen, for visual consistency)
    place(canvas, KEYBOARD_TOP_ROW, SCREEN_COL, "." + "-" * SCREEN_INNER_W + ".")
    place(canvas, KEYBOARD_ROW_IDX, SCREEN_COL, "|" + f["kb"] + "|")
    place(canvas, KEYBOARD_BOTTOM_ROW, SCREEN_COL, "'" + "-" * SCREEN_INNER_W + "'")

    # front lip: base is slightly deeper/wider than the screen, like a real clamshell
    lip_col = SCREEN_COL - 1
    lip_w = SCREEN_W + 2
    place(canvas, KEYBOARD_BOTTOM_ROW + 1, lip_col, "\\" + "_" * (lip_w - 2) + "/")

    return canvas_to_lines(canvas)


def build_frames():
    rng = random.Random(SEED)
    frames = []
    typed = [0, 0]

    for ch_i, full in enumerate(LINES_TO_TYPE):
        for n in range(1, len(full) + 1):
            typed[ch_i] = n
            kb = keyboard_frame(rng)
            frames.append(dict(typed=list(typed), cursor=True, kb=kb, arm=0, eyes=EYES_NORMAL, dur=FRAME_DUR, zzz=[]))
            if full[n - 1] == " ":
                kb2 = keyboard_frame(rng)
                frames.append(dict(typed=list(typed), cursor=True, kb=kb2, arm=0, eyes=EYES_NORMAL, dur=FRAME_DUR, zzz=[]))

    # hold + blink cursor, still typing pose
    for i in range(6):
        kb = keyboard_frame(rng)
        frames.append(dict(typed=list(typed), cursor=(i % 2 == 0), kb=kb, arm=0, eyes=EYES_NORMAL, dur=FRAME_DUR, zzz=[]))

    # tired: eyes droop, zzz's float up, hold, then perk back up
    still_kb1 = keyboard_frame(rng)
    for stage in range(len(ZZZ_STAGES)):
        frames.append(dict(typed=list(typed), cursor=False, kb=still_kb1, arm=0, eyes=EYES_TIRED, dur=TIRED_FRAME_DUR, zzz=ZZZ_STAGES[stage]))
    for _ in range(8):
        frames.append(dict(typed=list(typed), cursor=False, kb=still_kb1, arm=0, eyes=EYES_TIRED, dur=TIRED_FRAME_DUR, zzz=ZZZ_STAGES[-1]))
    for stage in reversed(range(len(ZZZ_STAGES))):
        frames.append(dict(typed=list(typed), cursor=False, kb=still_kb1, arm=0, eyes=EYES_TIRED, dur=TIRED_FRAME_DUR, zzz=ZZZ_STAGES[stage]))

    # gesture poses: phone call, shrug, point-up (idea), thinking -- each
    # holds for a beat, cut directly from one to the next
    for pose_name in ("phone", "shrug", "point", "think"):
        pose_kb = keyboard_frame(rng)
        pose_eyes = POSES[pose_name]["eyes"]
        for _ in range(GESTURE_HOLD_FRAMES):
            frames.append(dict(typed=list(typed), cursor=False, kb=pose_kb, arm=0, eyes=pose_eyes, dur=GESTURE_FRAME_DUR, zzz=[], pose=pose_name))

    # thumbs-up: raise arm through stages, look at viewer, hold, then lower
    still_kb = keyboard_frame(rng)
    for stage in range(len(ARM_UP_STAGES)):
        frames.append(dict(typed=list(typed), cursor=False, kb=still_kb, arm=stage, eyes=EYES_HAPPY, dur=THUMB_FRAME_DUR, zzz=[]))
    for _ in range(10):
        frames.append(dict(typed=list(typed), cursor=False, kb=still_kb, arm=len(ARM_UP_STAGES) - 1, eyes=EYES_HAPPY, dur=THUMB_FRAME_DUR, zzz=[]))
    for stage in reversed(range(len(ARM_UP_STAGES))):
        frames.append(dict(typed=list(typed), cursor=False, kb=still_kb, arm=stage, eyes=EYES_NORMAL, dur=THUMB_FRAME_DUR, zzz=[]))

    return frames


def build_svg(frame_data):
    scenes = [render_scene(f) for f in frame_data]
    durs = [f["dur"] for f in frame_data]
    n = len(scenes)
    n_cols = max(len(l) for scene in scenes for l in scene)
    n_rows = len(scenes[0])

    width = round(n_cols * CHAR_W) + 20
    height = round(n_rows * LINE_H) + 20
    total_dur = sum(durs)

    defs = (
        "\n  <defs>\n    <style>\n"
        "      .fr { font-family: 'JetBrains Mono','Liberation Mono','DejaVu Sans Mono',monospace;\n"
        f"            font-size: {FONT_SIZE}px; fill: {FILL}; white-space: pre; }}\n"
        "    </style>\n  </defs>"
    )

    # cumulative keytimes based on variable per-frame duration
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    keytimes = [round(c / total_dur, 6) for c in cum]

    body = []
    for i, scene in enumerate(scenes):
        tspans = "".join(
            f'<tspan x="10" dy="{LINE_H if li else 0}">{esc(line)}</tspan>'
            for li, line in enumerate(scene)
        )
        values = ["0"] * n
        values[i] = "1"
        values_attr = ";".join(values + [values[0]])
        keytimes_attr = ";".join(str(kt) for kt in keytimes)
        body.append(
            f'  <text y="18" class="fr" opacity="0">{tspans}'
            f'<animate attributeName="opacity" values="{values_attr}" '
            f'keyTimes="{keytimes_attr}" dur="{total_dur}s" begin="0s" '
            f'calcMode="discrete" repeatCount="indefinite"/>'
            f'</text>'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        f'  <rect width="100%" height="100%" fill="{BG}"/>{defs}\n'
        + "\n".join(body)
        + "\n</svg>"
    )
    return svg


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "laptop.svg"
    frame_data = build_frames()
    svg = build_svg(frame_data)
    with open(out, "w") as f:
        f.write(svg)
    total = sum(fr["dur"] for fr in frame_data)
    print(f"wrote {out}: {len(frame_data)} frames, ~{total:.1f}s loop")


if __name__ == "__main__":
    main()

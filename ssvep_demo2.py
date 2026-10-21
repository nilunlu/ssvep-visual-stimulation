from psychopy import visual, core, event
import numpy as np
import csv
import os
import time

# =====================================
# SSVEP VISUAL DEMO
# 4 / 8 / 16 TARGETS
# =====================================

TARGET_COUNT = 4       # 4, 8 veya 16
FULLSCREEN = False
WINDOW_SIZE = (1000, 750)

STIM_DURATION = 3.0    # saniye
REST_DURATION = 2.0
TRIALS_PER_TARGET = 2

# Frekanslar (Hz)
FREQUENCIES = [
    8.0, 8.5, 9.0, 9.5,
    10.0, 10.5, 11.0, 11.5,
    12.0, 12.5, 13.0, 13.5,
    14.0, 14.5, 15.0, 15.5
]

if TARGET_COUNT not in [4, 8, 16]:
    raise ValueError("TARGET_COUNT 4, 8 veya 16 olmali.")

frequencies = FREQUENCIES[:TARGET_COUNT]

# =====================================
# WINDOW
# =====================================

win = visual.Window(
    size=WINDOW_SIZE,
    fullscr=FULLSCREEN,
    units="height",
    color=(-0.5, -0.5, -0.5),
    waitBlanking=True,
    allowGUI=True
)

win.recordFrameIntervals = True

actual_refresh = win.getActualFrameRate()

if actual_refresh is None:
    print("UYARI: Ekran yenileme hizi olculemedi.")
else:
    print(f"Olculen yenileme hizi: {actual_refresh:.3f} Hz")

# =====================================
# TARGET POSITIONS
# =====================================

if TARGET_COUNT == 4:
    cols = 2
elif TARGET_COUNT == 8:
    cols = 4
else:
    cols = 4

rows = TARGET_COUNT // cols

if TARGET_COUNT == 4:
    spacing_x = 0.40
    spacing_y = 0.34
    target_width = 0.28
    target_height = 0.24

elif TARGET_COUNT == 8:
    spacing_x = 0.22
    spacing_y = 0.34
    target_width = 0.18
    target_height = 0.24

else:  # 16 hedef
    spacing_x = 0.22
    spacing_y = 0.19
    target_width = 0.18
    target_height = 0.15

positions = []

for i in range(TARGET_COUNT):
    col = i % cols
    row = i // cols

    x = (col - (cols - 1) / 2) * spacing_x
    y = ((rows - 1) / 2 - row) * spacing_y

    positions.append((x, y))

# =====================================
# CREATE STIMULI
# =====================================

targets = []
labels = []

for i in range(TARGET_COUNT):

    rect = visual.Rect(
        win,
        width=target_width,
        height=target_height,
        pos=positions[i],
        fillColor=(1, 1, 1),
        lineColor=(0.5, 0.5, 0.5),
        colorSpace="rgb"
    )

    label = visual.TextStim(
        win,
        text=f"{i + 1}\n{frequencies[i]} Hz",
        pos=positions[i],
        height=0.022,
        color="red"
    )

    targets.append(rect)
    labels.append(label)

instruction = visual.TextStim(
    win,
    text="SSVEP TEST\n\nSPACE: Baslat\nESC: Cikis",
    color="white",
    height=0.045,
    pos=(0, 0)
)

status = visual.TextStim(
    win,
    text="",
    color="white",
    height=0.027,
    pos=(0, 0.43)
)

# =====================================
# CSV LOGGING
# =====================================

filename = f"ssvep_{TARGET_COUNT}_targets_{int(time.time())}.csv"

logfile = open(filename, "w", newline="")
writer = csv.writer(logfile)

writer.writerow([
    "trial",
    "target",
    "frequency",
    "frame",
    "time",
    "frame_interval"
])

# =====================================
# FUNCTIONS
# =====================================

def check_escape():
    if "escape" in event.getKeys():
        logfile.close()
        win.close()
        core.quit()


def draw_targets(t, selected_target=None):

    for i in range(TARGET_COUNT):

        frequency = frequencies[i]

        # Sinusoidal luminance modulation
        brightness = -0.35 + 0.25 * np.sin(
    2 * np.pi * frequency * t)

        targets[i].fillColor = (
            brightness,
            brightness,
            brightness
        )

        targets[i].draw()
        labels[i].draw()

    if selected_target is not None:
        status.text = (
            f"Hedef: {selected_target + 1} | "
            f"Frekans: {frequencies[selected_target]} Hz"
        )
        status.draw()


# =====================================
# INTRO SCREEN
# =====================================

instruction.draw()
win.flip()

event.clearEvents()

while True:
    keys = event.getKeys()

    if "space" in keys:
        break

    if "escape" in keys:
        logfile.close()
        win.close()
        core.quit()

    core.wait(0.01)

# =====================================
# EXPERIMENT
# =====================================

try:

    trial_number = 0

    for target_index in range(TARGET_COUNT):

        for repeat in range(TRIALS_PER_TARGET):

            trial_number += 1

            # -------------------------
            # REST
            # -------------------------

            rest_text = visual.TextStim(
                win,
                text=(
                    f"Sonraki hedef: {target_index + 1}\n\n"
                    "Hazirlan..."
                ),
                color="white",
                height=0.04
            )

            rest_clock = core.Clock()

            while rest_clock.getTime() < REST_DURATION:

                check_escape()

                rest_text.draw()
                win.flip()

            # -------------------------
            # STIMULATION
            # -------------------------

            stim_clock = core.Clock()

            frame_number = 0

            # Synchronize clock with first flip
            win.callOnFlip(stim_clock.reset)
            draw_targets(0, target_index)
            win.flip()

            previous_t = 0.0

            while True:

                check_escape()

                t = stim_clock.getTime()

                if t >= STIM_DURATION:
                    break

                draw_targets(t, target_index)
                win.flip()

                current_t = stim_clock.getTime()
                interval = current_t - previous_t

                writer.writerow([
                    trial_number,
                    target_index + 1,
                    frequencies[target_index],
                    frame_number,
                    current_t,
                    interval
                ])

                previous_t = current_t
                frame_number += 1

            logfile.flush()

    # =====================================
    # FINISH
    # =====================================

    finish = visual.TextStim(
        win,
        text="DENEY TAMAMLANDI\n\nESC: Cikis",
        color="white",
        height=0.045
    )

    while True:

        finish.draw()
        win.flip()

        if "escape" in event.getKeys():
            break

finally:

    logfile.close()

    print("Deney tamamlandi.")
    print("CSV dosyasi:", os.path.abspath(filename))
    print("Kaydedilen kare sayisi:", len(win.frameIntervals))

    win.close()

core.quit()
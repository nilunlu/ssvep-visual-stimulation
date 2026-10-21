"""SSVEP 4-target frame-locked visual stimulus and software validation.

PsychoPy Coder -> Open -> Run. Space starts, Escape exits.
Output CSVs are saved in ~/Documents/SSVEP_Results.
This does not measure emitted light; use photodiode to validate hardware output.
"""
import csv
import datetime
import math
from pathlib import Path

import numpy as np
from psychopy import core, event, visual

TARGET_FREQUENCIES = (8.0, 8.5, 9.0, 9.5)
REFERENCE_REFRESH_HZ = 60.0  # explicitly selected macOS display mode
DURATION_SECONDS = 12.0
MEAN_RGB = -0.35
AMPLITUDE_RGB = 0.25
OUTPUT_DIR = Path.home() / 'Documents' / 'SSVEP_Results'


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    frames_path = OUTPUT_DIR / f'ssvep_frequency_frames_{stamp}.csv'
    summary_path = OUTPUT_DIR / f'ssvep_frequency_summary_{stamp}.csv'

    win = visual.Window(size=(1100, 800), fullscr=False, units='height',
                        color=(-0.55, -0.55, -0.55), colorSpace='rgb',
                        waitBlanking=True, allowGUI=True)
    win.recordFrameIntervals = True
    positions = [(-0.21, 0.16), (0.21, 0.16), (-0.21, -0.16), (0.21, -0.16)]
    squares = [visual.Rect(win, pos=pos, width=0.28, height=0.24,
                           fillColor=(MEAN_RGB,) * 3, lineColor=(-0.10,) * 3,
                           colorSpace='rgb') for pos in positions]
    labels = [visual.TextStim(win, text=f'{i+1}: {f:g} Hz', pos=pos,
                              color='white', height=0.025)
              for i, (pos, f) in enumerate(zip(positions, TARGET_FREQUENCIES))]
    note = visual.TextStim(win, text='4 hedefli SSVEP frekans testi\nSPACE: Baslat    ESC: Cikis',
                           pos=(0, 0.38), height=0.030, color='white')

    try:
        while True:
            note.draw()
            win.flip()
            keys = event.getKeys()
            if 'escape' in keys:
                return
            if 'space' in keys:
                break
            core.wait(0.01)
        event.clearEvents()
        # Disable frame logging during intro; start logging only stimulus flips.
        win.frameIntervals = []
        win.nDroppedFrames = 0
        nframes = int(round(DURATION_SECONDS * REFERENCE_REFRESH_HZ))
        brightness_data = []
        timestamp_data = []
        t0 = None
        for frame_index in range(nframes):
            if 'escape' in event.getKeys():
                break
            values = []
            for freq, square, label in zip(TARGET_FREQUENCIES, squares, labels):
                value = MEAN_RGB + AMPLITUDE_RGB * math.sin(
                    2.0 * math.pi * freq * frame_index / REFERENCE_REFRESH_HZ
                )
                square.fillColor = (value, value, value)
                square.draw()
                label.draw()
                values.append(value)
            win.flip()
            now = core.getTime()
            if t0 is None:
                t0 = now
            brightness_data.append(values)
            timestamp_data.append(now - t0)

        values_array = np.asarray(brightness_data, dtype=float)
        timestamps = np.asarray(timestamp_data, dtype=float)
        intervals = np.diff(timestamps)
        median_interval = float(np.median(intervals)) if len(intervals) else float('nan')
        effective_rate = 1.0 / median_interval if median_interval > 0 else float('nan')
        long_intervals = int(np.sum(intervals > 1.5 / REFERENCE_REFRESH_HZ))
        frame_count = len(timestamps)
        with frames_path.open('w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['frame', 'flip_time_s', 'interval_from_previous_flip_ms',
                             'target1_8Hz_rgb', 'target2_8_5Hz_rgb',
                             'target3_9Hz_rgb', 'target4_9_5Hz_rgb'])
            for i in range(frame_count):
                interval_ms = (timestamps[i] - timestamps[i-1]) * 1000 if i else ''
                writer.writerow([i, f'{timestamps[i]:.7f}',
                                 f'{interval_ms:.5f}' if i else '',
                                 *[f'{v:.7f}' for v in values_array[i]]])

        summaries = []
        # FFT of programmed brightness sequence using the nominal frame rate.
        # This checks discrete-time signal design, NOT actual optical modulation.
        if frame_count >= 4:
            spectrum_freqs = np.fft.rfftfreq(frame_count, d=1.0 / REFERENCE_REFRESH_HZ)
            for j, target in enumerate(TARGET_FREQUENCIES):
                x = values_array[:, j] - np.mean(values_array[:, j])
                amplitudes = np.abs(np.fft.rfft(x))
                if len(amplitudes) > 1:
                    amplitudes[0] = 0
                    peak = float(spectrum_freqs[np.argmax(amplitudes)])
                else:
                    peak = float('nan')
                summaries.append((target, peak, peak-target))

        with summary_path.open('w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['target_frequency_hz', 'fft_peak_programmed_hz',
                             'frequency_difference_hz', 'recorded_frames',
                             'median_flip_interval_ms', 'estimated_flip_rate_hz',
                             'intervals_over_1_5_expected_frames'])
            for intended, measured, diff in summaries:
                writer.writerow([intended, round(measured, 5), round(diff, 5),
                                 frame_count, round(median_interval * 1000, 5),
                                 round(effective_rate, 5), long_intervals])

        result = visual.TextStim(
            win, color='white', height=0.026,
            text=(f'Test tamamlandi — {frame_count} kare\n'
                  f'Medyan kare suresi: {median_interval*1000:.3f} ms\n'
                  f'Tahmini yenileme: {effective_rate:.3f} Hz\n'
                  f'Uzun kare araligi (>25 ms): {long_intervals}\n\n'
                  'CSV kayitlari: Documents / SSVEP_Results\n\nESC: Cikis'),
            wrapWidth=1.2)
        while 'escape' not in event.getKeys():
            result.draw()
            win.flip()
            core.wait(0.01)
        print('Frames:', frames_path)
        print('Summary:', summary_path)
    finally:
        win.close()


if __name__ == '__main__':
    main()

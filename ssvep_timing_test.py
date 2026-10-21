"""4-target SSVEP frame-timing diagnostic. No EEG connection."""
import csv
import math
from datetime import datetime
from pathlib import Path
from statistics import median

from psychopy import core, event, visual

# Comfortable visual settings used for the initial demo.
FREQUENCIES_HZ = (8.0, 8.5, 9.0, 9.5)
MEAN_RGB = -0.35
AMPLITUDE_RGB = 0.25
DURATION_S = 12.0
WINDOW_SIZE = (1000, 750)
FULLSCREEN = False


def main():
    log_path = Path.home() / 'Documents' / ('ssvep_timing_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv')
    log_path.parent.mkdir(parents=True, exist_ok=True)
    win = visual.Window(size=WINDOW_SIZE, fullscr=FULLSCREEN, units='height',
                        color=(-0.5, -0.5, -0.5), waitBlanking=True, allowGUI=True)
    win.recordFrameIntervals = True
    positions = [(-0.20, 0.17), (0.20, 0.17), (-0.20, -0.17), (0.20, -0.17)]
    squares = [visual.Rect(win, width=0.28, height=0.24, pos=p,
                           fillColor=(MEAN_RGB,) * 3, lineColor=(0.1,) * 3,
                           colorSpace='rgb') for p in positions]
    labels = [visual.TextStim(win, text=f'{i+1}\n{f} Hz', pos=p,
                              color='red', height=0.027) for i, (p, f) in enumerate(zip(positions, FREQUENCIES_HZ))]
    header = visual.TextStim(win, text='SSVEP 4 TARGETS - FRAME TIMING TEST',
                             pos=(0, 0.43), height=0.029, color='white')
    instructions = visual.TextStim(win, text='SPACE: start 12-second test     ESC: cancel',
                                   pos=(0, -0.39), color='white', height=0.026)
    def draw(t):
        for f, rect, label in zip(FREQUENCIES_HZ, squares, labels):
            lum = MEAN_RGB + AMPLITUDE_RGB * math.sin(2.0 * math.pi * f * t)
            rect.fillColor = (lum, lum, lum)
            rect.draw()
            label.draw()
        header.draw()

    try:
        event.clearEvents()
        while True:
            header.draw()
            instructions.draw()
            for rect, label in zip(squares, labels):
                rect.draw()
                label.draw()
            win.flip()
            keys = event.getKeys()
            if 'escape' in keys:
                print('Test cancelled before start.')
                return
            if 'space' in keys:
                break

        # t=0 is attached to the first stimulus flip; time is sampled just before each subsequent flip.
        clock = core.Clock()
        win.recordFrameIntervals = False
        draw(0.0)
        win.callOnFlip(clock.reset)
        first_flip = win.flip()
        win.recordFrameIntervals = True
        records = []
        frame = 0
        while True:
            if 'escape' in event.getKeys():
                print('Test cancelled; partial timing data will be saved.')
                break
            t_before_flip = clock.getTime()
            if t_before_flip >= DURATION_S:
                break
            draw(t_before_flip)
            timestamp = win.flip()  # PsychoPy flip time, not a photodiode measurement.
            frame += 1
            records.append((frame, t_before_flip, timestamp))

        with log_path.open('w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['frame', 'stimulus_time_s_before_flip', 'psychopy_flip_timestamp_s',
                             'interval_s_from_previous_flip'])
            previous = first_flip
            intervals = []
            for number, stimulus_time, flip_time in records:
                interval = flip_time - previous
                intervals.append(interval)
                writer.writerow([number, f'{stimulus_time:.6f}', f'{flip_time:.6f}', f'{interval:.6f}'])
                previous = flip_time

        print('\n----- SSVEP FRAME TIMING -----')
        print('CSV:', log_path)
        print('Number of displayed frames:', len(records))
        if intervals:
            typical = median(intervals)
            threshold = 1.5 * typical
            long_frames = sum(dt > threshold for dt in intervals)
            print(f'Median frame interval: {typical * 1000:.3f} ms')
            print(f'Estimated effective refresh: {1 / typical:.3f} Hz')
            print(f'Max frame interval: {max(intervals) * 1000:.3f} ms')
            print(f'Intervals > 1.5x median: {long_frames} / {len(intervals)}')
            print('Note: software flip timestamps cannot prove exact luminance frequencies.')
            summary = (f'Median: {typical*1000:.2f} ms | approx. {1/typical:.2f} Hz\n'
                       f'Long intervals: {long_frames}/{len(intervals)}\n\nCSV saved to Documents\n\nESC: close')
        else:
            summary = 'No frames recorded. ESC: close'
        result_text = visual.TextStim(win, text=summary, color='white', height=0.037,
                                      wrapWidth=0.9)
        event.clearEvents()
        while 'escape' not in event.getKeys():
            result_text.draw()
            win.flip()
            core.wait(0.01)
    finally:
        win.close()
        core.quit()


if __name__ == '__main__':
    main()

import os
import time
from argparse import ArgumentParser
from datetime import datetime
from statistics import fmean

import cv2


class AppError(Exception):
    pass


def record(cap, segment_duration, out):
    start_time = time.time()
    while int(time.time() - start_time) < segment_duration:
        ret, frame = cap.read()
        if not ret:
            raise AppError("Could not get frame to record")
        out.write(frame)


def loop(url, output_dir, segment_duration, trig_mean, trig_std):
    cap = cv2.VideoCapture(url)
    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)

    exit_requested = False

    old_frame_cropped = None
    try:
        while not exit_requested:
            ret, frame = cap.read()
            if not ret:
                raise AppError("Could not get frame")
            frame_cropped = frame[int(h * 0.1):int(h), :]
            if old_frame_cropped is None:
                old_frame_cropped = frame_cropped

            delta_frame = cv2.absdiff(old_frame_cropped, frame_cropped)
            (delta_means, delta_stds) = cv2.meanStdDev(delta_frame)
            delta_means = fmean(delta_means)
            delta_stds = fmean(delta_stds)
            start_record = False
            if delta_means > trig_mean or delta_stds > trig_std:
                start_record = True
            if not start_record:
                continue
            dt = datetime.now().isoformat().replace(':', '-').replace('.', '-')
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(f"{output_dir}/output_{dt}.mp4", fourcc, fps, (int(w), int(h)))
            try:
                print(f"{dt} triggering {delta_means=} {delta_stds=}")
                record(cap, segment_duration, out)
                print(f"End of record triggered at {dt}")

            finally:
                out.release()

    except cv2.error as e:
        print('CV2 error:', e)
    except AppError as e:
        print(e)
    except Exception as e:
        print('Error', e)
    else:
        print("No problem reported")

    cap.release()

    return exit_requested


def run(url, output_dir, segment_duration, trig_mean, trig_std):
    exit_requested = False

    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    while not exit_requested:
        exit_requested = loop(url, output_dir, segment_duration, trig_mean, trig_std)
        if exit_requested:
            break

        list_of_files = os.listdir(output_dir)
        full_path = [f"{output_dir}/{x}" for x in list_of_files]

        if len(list_of_files) == 15:
            oldest_file = min(full_path, key=os.path.getctime)
            os.remove(oldest_file)

    cv2.destroyAllWindows()


def main():
    parser = ArgumentParser()
    parser.add_argument("url", help="url of rtsp stream")
    parser.add_argument("--output", default='videos', help="output directory")
    parser.add_argument("--segment", default=60, type=int, help="record duration")
    parser.add_argument("--trig-mean", default=10, type=int, help="minium delta mean to trigger")
    parser.add_argument("--trig-std", default=10, type=int, help="minium delta std to trigger")
    args = parser.parse_args()
    run(args.url, args.output, args.segment, args.trig_mean, args.trig_std)


if __name__ == '__main__':
    main()

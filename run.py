import os
import time
from argparse import ArgumentParser
from datetime import datetime

import cv2


def loop(url, output_dir, segment_duration):
    cap = cv2.VideoCapture(url)

    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    dt = datetime.now().isoformat().replace(':', '-').replace('.', '-')
    out = cv2.VideoWriter(f"{output_dir}/output_{dt}.mp4", fourcc, fps, (int(w), int(h)))

    exit_requested = False
    try:
        start_time = time.time()
        while int(time.time() - start_time) < segment_duration:
            ret, frame = cap.read()
            if not ret:
                break

            out.write(frame)

            cv2.imshow('frame', frame)

            if cv2.waitKey(1) == ord('q'):
                exit_requested = True
                break

    except cv2.error as e:
        print('CV2 error:', e)
    except Exception as e:
        print('Error', e)
    else:
        print("No problem reported")
    finally:
        out.release()

    cap.release()

    return exit_requested


def run(url, output_dir, segment_duration):
    exit_requested = False

    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    while not exit_requested:
        exit_requested = loop(url, output_dir, segment_duration)
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
    parser.add_argument("--segment", default=60, type=int, help="video segment duration")
    args = parser.parse_args()
    run(args.url, args.output, args.segment)


if __name__ == '__main__':
    main()

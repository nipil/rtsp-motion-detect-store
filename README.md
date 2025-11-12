# rtsp-motion-detect-store

Captures an RTSP stream, diffs,and if above threshold, records to mp4 for a while

    docker run --rm -it -v .\output\:/videos nipil/rtsp-motion-detect-store rtsp://user:pass@ip

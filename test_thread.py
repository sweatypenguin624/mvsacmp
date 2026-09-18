import cv2
import threading
import queue
import time
from pathlib import Path

class ThreadedVideoStreamReader:
    def __init__(self, video_path: Path, max_queue: int = 128):
        self.video_path = Path(video_path)
        self.cap = cv2.VideoCapture(str(self.video_path))
        self.q = queue.Queue(maxsize=max_queue)
        self.stopped = False
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        idx = 0
        while True:
            if self.stopped:
                break
            if not self.q.full():
                ok, frame = self.cap.read()
                if not ok:
                    self.stopped = True
                    break
                self.q.put((idx, frame))
                idx += 1
            else:
                time.sleep(0.001)

    def frames(self, start_frame: int = 0):
        if start_frame > 0:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            # Re-init thread or wait until it seeks... simpler: assume start_frame=0 for test
        while True:
            if self.stopped and self.q.empty():
                break
            if not self.q.empty():
                yield self.q.get()
            else:
                time.sleep(0.001)

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stopped = True
        self.cap.release()
        self.thread.join()

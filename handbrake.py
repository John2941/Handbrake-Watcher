import queue
import os
import threading
import time
from watchdog.events import FileSystemEventHandler
from media import Media
import hashlib


class Handbrake(FileSystemEventHandler):
    def __init__(self, args=None):
        self.args = args
        self.transcode_queue = queue.Queue()
        self.active_transcoding_queue = []
        self.transcode_obj = ''
        self.thread = None
        self.transcoder_active = False
        self.new_event = False
        self.start()


    def on_created(self, event):
        if event.is_directory:
            print(f'dir event created ... waiting {self.args.time} seconds before adding to queue')
            time.sleep(self.args.time)  # gonna have to wait an arbitrary amount since I can't tell when a copy operation has fnished
            new_transcode = event.src_path
            self.add_to_queue(new_transcode)

    def add_to_queue(self, new_transcode):
        video_file_ext = ['.mkv','.mp4','.avi', '.mpegts', '.flv']
        if os.path.exists(new_transcode):
            for path, dirs, files in os.walk(new_transcode):
                for file in files:
                    filename, fileext = os.path.splitext(file)
                    if fileext in video_file_ext:
                        full_video_path = os.path.join(path, file)
                        new_transcode = Media(full_video_path, args=self.args)
                        print(f'Found video file to add to queue {full_video_path}')
                        self.transcode_queue.put(new_transcode)

    def start(self):
        self.handbrake_thread = threading.Thread(target=self.run, name='Handbrake')
        self.handbrake_thread.daemon = True
        self.handbrake_thread.start()

    def run(self):
        while True:
            if not self.transcode_queue.empty():
                if len(self.active_transcoding_queue) == 0:
                    #  probaly should leave this on the queue, until successfully overwritten the orginial transcoded file
                    media = self.transcode_queue.get()
                    self.active_transcoding_queue.append(media)
                    print('Found file to transcode.')
                    media.start_transcode()
                    self.transcoder_active = media
                else:
                    transcoding_thread = self.active_transcoding_queue[0]
                    if transcoding_thread.transcoding_completed:
                        self.active_transcoding_queue.remove(transcoding_thread)
                    print('Items in the queue, but an item is currently being transcoded. Waiting till that is finished.')
            else:
                print('No items on the handbrake queue')
            time.sleep(5)



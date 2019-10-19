import os
from subprocess import Popen, PIPE, STDOUT
import threading
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata


class Media():
    def __init__(self, video_file, args=None):
        self.args = args
        if os.path.exists(video_file):
            self.orig_video_abs_path = video_file
        else:
            raise FileNotFoundError

        self.orig_dir, self.orig_video_filename = os.path.split(self.orig_video_abs_path)
        self.transcoded_dir = self.args.transcode_dir
        self.orig_video_filename_no_ext = os.path.splitext(self.orig_video_filename)[0]
        self.transcoded_video_abs_path = os.path.join(
            self.transcoded_dir,
            self.orig_video_filename_no_ext + '.mkv'
        )
        self.currently_being_transcoded = False
        self.transcoding_completed = False
        self.metadata = self._get_metadata()
        self._check_4k()


    def is_media_uhd(self):
        height = int(self.metadata['Video stream']['Image height'].split(' ')[0])
        if height > 1080:
            return True
        else:
            return False

    def _get_metadata(self):
        p = createParser(self.orig_video_abs_path)
        metadata = extractMetadata(p)
        return metadata.exportDictionary()

    def _check_4k(self):
        if self.is_media_uhd():
            if self.args.process_uhd:
                pass
            else:
                raise Exception('Media is UHD.')
        else:
            pass

    def start_transcode(self):
        self.transcode_thread = threading.Thread(target=self.transcode, name='Transcode')
        self.transcode_thread.daemon = True
        self.transcode_thread.start()

    def transcode(self):
        self.currently_being_transcoded = True
        cmd = [
            self.args.handbrake_path,
            '--disable-qsv-decoding',
            '--preset-import-file',
            f'{self.args.preset_path}',
            '-Z',
            f'{self.args.preset_name}',
            '-i',
            self.orig_video_abs_path,
            '-o',
            self.transcoded_video_abs_path
        ]
        print(f'Running {" ".join(cmd)}')

        p = Popen(
            cmd,
            stdout=PIPE,
            stderr=STDOUT
        )
        while True:
            out = p.stdout.readline()
            if out == '' and p.poll() is not None:
                break
            if out:
                print(out)
        #p.wait()
        self.currently_being_transcoded = False
        self._replace_orig_file()
        print('Done running')

    def _replace_orig_file(self):
        # move the orig file to <orig_name>.old
        print('Renaming')
        os.rename(self.orig_video_abs_path, os.path.join(self.orig_video_abs_path + '.old'))
        # move the trancoded file
        os.rename(
            self.transcoded_video_abs_path,
            os.path.join(
                self.orig_dir,
                os.path.split(self.transcoded_video_abs_path)[1]
            )
        )
        self.transcoding_completed = True



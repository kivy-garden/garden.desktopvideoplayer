from subprocess import Popen, PIPE, STDOUT
import os
import threading


class FFmpegCLI:

    def __init__(self, ffmpeg_bin='ffmpeg', ffprobe_bin='ffprobe'):
        self.ffmpeg_bin = ffmpeg_bin
        self.ffprobe_bin = ffprobe_bin

    def _run_in_thread(self, target, args, callback=None):
        t = threading.Thread(target=target, args=[args, callback])
        t.start()

    def _run_cmd(self, proc_args, callback):
        # if outbuff is None:
        #     outbuff = open(os.devnull, 'wb')
        proc = Popen(proc_args, stdout=PIPE, stderr=PIPE)
        proc.wait()
        stdout, strerr = proc.communicate()

        if callback:
            callback(proc.returncode, stdout, strerr)
        # outbuff.close()

    def is_available(self, callback):
        self._run_in_thread(self._run_cmd, [self.ffmpeg_bin, '-version'], callback)

    def take_screenshot(self, file, seconds, dest, callback=None, frames=1, quality=1):
        self._run_in_thread(self._run_cmd, [self.ffmpeg_bin,
            '-ss', str(seconds),
            '-i', file,
            '-y',
            '-qscale:v', str(quality),
            '-vframes', str(frames),
            dest
        ], callback)

    def get_info(self, file, callback):
        self._run_in_thread(self._run_cmd, [self.ffprobe_bin,
            '-i', file,
        ], callback)
import re
import threading
from subprocess import Popen, PIPE


class FFmpegCLI:
    def __init__(self, ffmpeg_bin='ffmpeg', ffprobe_bin='ffprobe'):
        self.ffmpeg_bin = ffmpeg_bin
        self.ffprobe_bin = ffprobe_bin

    def _run_in_thread(self, target, args, callback=None):
        t = threading.Thread(target=target, args=[args, callback])
        t.start()

    def _run_cmd(self, proc_args, callback):
        try:
            proc = Popen(proc_args, stdout=PIPE, stderr=PIPE)
        except OSError:
            callback(None, None, None)
            return

        proc.wait()
        stdout, strerr = proc.communicate()

        if callback:
            callback(proc.returncode, stdout, strerr)
            # outbuff.close()

    def is_available(self, callback):
        self.version(lambda code, out, err: callback(code == 0))

    def version(self, callback):
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

    def get_info(self, file, callback, trim_ffprobe_info=True):
        def _trim_response(code, out, err):
            if trim_ffprobe_info:
                # Match everything after ffrobe verison info
                err = re.match(r"ffprobe (.|\n)+(Input(.|\n)*)", err, re.MULTILINE).group(2)
            # Logger.info(code)
            # Logger.info(out)
            # Logger.info(err)
            callback(code, out, err)

        self._run_in_thread(self._run_cmd, [self.ffprobe_bin,
                                            '-i', file,
                                            ], _trim_response)

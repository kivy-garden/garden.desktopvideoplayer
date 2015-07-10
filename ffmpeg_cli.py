from subprocess import Popen

# FFMPEG_BIN = 'ffmpeg'
# FFPROBE_BIN = 'ffprobe'

class FFmpegCLI:

    def __init__(self, ffmpeg_bin='ffmpeg'):
        self.ffmpeg_bin = ffmpeg_bin

    def is_available(self):
        proc = Popen(self.ffmpeg_bin, ['-version'])
        return proc.returncode == 0


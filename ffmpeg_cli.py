from subprocess import Popen

# FFMPEG_BIN = 'ffmpeg'
# FFPROBE_BIN = 'ffprobe'

class FFmpegCLI:

    def __init__(self, ffmpeg_bin='ffmpeg'):
        self.ffmpeg_bin = ffmpeg_bin

    def is_available(self):
        proc = Popen(self.ffmpeg_bin, ['-version'])
        return proc.returncode == 0

    def take_screenshot(self, file, time, dest):
        proc = Popen([self.ffmpeg_bin,
            '-ss', time,
            '-i', file,
            '-y',
            '-v:b', '3',
            '-vframes', '1',
            # '-s', '240x200',
            dest
        ])

import subprocess
import socket
import os
import signal
class streamer :

    ffmpeg_pid = None
    LIVE_SIGNAL = bytearray([0x01])

    MACOS_FACETIME_PRESET = 'ffmpeg -r 30 -s 640x480 -an -f avfoundation -i 0 -f mpegts udp://{remote_model_url}:{stream_port}'

    flags = None
    response_callback = None

    def __init__(self, remote_model_url, control_port=7777 ,stream_port=8888):
        self.remote_model_url = remote_model_url
        self.control_port = control_port
        self.stream_port = stream_port
        self.socket =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = (remote_model_url, control_port)

    def set_ffmpeg_flag(self, flags):
        self.flags = flags

    def set_model_respones_callback(self, response_callback):
        self.response_callback = response_callback


    def start(self):


        cmd = self.flags.format(remote_model_url=self.remote_model_url, stream_port=self.stream_port)

        self.ffmpeg_pid = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid())

        while True:
            self.socket.sendto(self.LIVE_SIGNAL, self.address)

            recv_data, address = self.socket.recvfrom(128)

            self.response_callback(streamer=self, recv_data=recv_data)


    def stop(self):
        os.killpg(os.getpgid(self.ffmpeg_pid.pid), signal.SIG_TERM)


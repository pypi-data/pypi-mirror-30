import cv2
import socket

class remote_model:

    class error(Exception):
        def __str__(self):
            return 'dats error :'

    class no_loop_processor_error(error):
        def _str__(self):
            return super.__str__() + 'no loop processor'


    BUFFER_SIZE = 4

    loop_processor = None
    cap = None

    def __init__(self, addr = 'localhost', command_port=7777, stream_port=8888):
        self.command_port = command_port
        self.stream_port = stream_port
        self.bind_addr = addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((addr, self.command_port))

    def set_loop_processor(self, func):
        self.loop_processor = func

    def open(self):

        if None == self.loop_processor :
            raise self.no_loop_processor_error()

        self.cap = cv2.VideoCapture('udp://{address}:{port}'.format(address=self.bind_addr, port=self.stream_port))

        while True :
            ret, frame = self.cap.read()

            recv_data, address = self.socket.recvfrom(self.BUFFER_SIZE)

            to_send = self.loop_processor(server=self, stream_frame=frame, recv_data=recv_data)

            self.socket.sendto(to_send, address)


    def close(self):
        self.socket.close()
        self.cap.release()

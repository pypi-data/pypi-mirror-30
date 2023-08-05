from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from time import sleep

dirs = [{'x': 0, 'y': 1.797e308}, {'x': 0, 'y': -10e306}, {'x': 10e306, 'y': 0}, {'x': -10e306, 'y': 0}]

MAX_FAR_DIRECTION = 1.797e308
RIGHT = {'x': MAX_FAR_DIRECTION, 'y': 0}
LEFT = {'x': -MAX_FAR_DIRECTION, 'y': 0}
UP = {'x': 0, 'y': MAX_FAR_DIRECTION}
DOWN = {'x': 0, 'y': -MAX_FAR_DIRECTION}

# io = SocketIO('0.0.0.0', 3000)
#

def setup_handler(data):
    print(data)

# io.on('gameSetup', setup_handler)
# #
# io.emit('gotit', {
#     'id': io._engineIO_session.id,
#     'target': {'x': 0, 'y': 0}
# })

# while True:
#     for d in dirs:
#         print(d)
#         io.emit('heartbeat', d)
#         sleep(1)

        # for _ in range(200):
        #     io.emit('heartbeat', {
        #         'id': io._engineIO_session.id,
        #         'x': 0, 'y': 0
        #     })



# io.wait()

class BotClient:
    MAX_FAR_DIRECTION = 1.797e308
    RIGHT = {'x': MAX_FAR_DIRECTION, 'y': 0}
    LEFT = {'x': -MAX_FAR_DIRECTION, 'y': 0}
    UP = {'x': 0, 'y': MAX_FAR_DIRECTION}
    DOWN = {'x': 0, 'y': -MAX_FAR_DIRECTION}

    def __init__(self, name, speed_rate=1.0, host='0.0.0.0', port=3000):
        self.host = host
        self.port = port
        self.socket = SocketIO(host, port)
        self.socket_id = self.socket._engineIO_session.id

        self.name = name
        self.speed_rate = speed_rate

        print('[INFO] - Bot {} has started on port {}'.format(name, port))

        self.socket.on('gameSetup', setup_handler)
#         self.socket.on('serverTellPlayerMove', setup_handler)
        self._got_it()
#
#     # def on(self):
#
#
    def server_tell_handler(self, data):
        print(1)
        print(data)

    def _got_it(self):
        self.socket.emit('gotit', {
            'id': self.socket_id,
            'name': self.name,
            'target': {'x': 0, 'y': 0},
            'screenWidth': 1000,
            'screenHeight': 1000
        })

    def move_right(self):
        self.socket.emit('heartbeat', self.RIGHT)
        sleep(self.speed_rate)

    def move_left(self):
        self.socket.emit('heartbeat', self.LEFT)
        sleep(self.speed_rate)

    def move_up(self):
        self.socket.emit('heartbeat', self.UP)
        sleep(self.speed_rate)

    def move_down(self):
        self.socket.emit('heartbeat', self.DOWN)
        sleep(self.speed_rate)


b = BotClient('prettygoo', speed_rate=1)

while True:
    b.move_left()
    b.move_up()
    b.move_right()
    b.move_down()

from socketIO_client import SocketIO
from time import sleep


class GameBoard:
    def __init__(self):
        self.visible_cells = []
        self.visible_food = []
        self.visible_mass = []

    def update(self, args):
        print(len(args[0]), len(args[1]), len(args[2]))
        self.update_visible_cells(args[0])
        self.update_visible_food(args[1])
        self.update_visible_mass(args[2])

    def update_visible_cells(self, new_visible_cells):
        self.visible_cells = new_visible_cells

    def update_visible_food(self, new_visible_food):
        self.visible_food = new_visible_food

    def update_visible_mass(self, new_visible_mass):
        self.visible_mass = new_visible_mass


class BotClient:
    MAX_FAR_DIRECTION = 1.797e308
    RIGHT = {'x': MAX_FAR_DIRECTION, 'y': 0}
    LEFT = {'x': -MAX_FAR_DIRECTION, 'y': 0}
    UP = {'x': 0, 'y': MAX_FAR_DIRECTION}
    DOWN = {'x': 0, 'y': -MAX_FAR_DIRECTION}

    enable_logging = True

    def __init__(self, botname, speed_rate=1, wait_rate=0.1, host='0.0.0.0', port=3000, enable_logging=True):
        self.host = host
        self.port = port
        self.socket = SocketIO(host, port)
        self.socket_id = self.socket._engineIO_session.id
        self.enable_logging = enable_logging

        self.name = botname
        self.speed_rate = speed_rate
        self.wait_rate = wait_rate

        self.board = GameBoard()

        print('[INFO] - Bot {} has started on port {}'.format(botname, port))

        self.enable_on()
        self.init_socket_communication()

    def enable_on(self):
        self.socket.on('serverTellPlayerMove', self.server_tell_handler)

    def server_tell_handler(self, *args):
        print('[INFO] - game board entities have been updated')
        self.board.update(args)

    def init_socket_communication(self):
        self.socket.emit('gotit', {
            'id': self.socket_id,
            'name': self.name,
            'target': {'x': 0, 'y': 0},
            'screenWidth': 1000,
            'screenHeight': 1000
        })
        self.socket.wait(self.wait_rate)

    def move_right(self):
        self.socket.emit('heartbeat', self.RIGHT)
        sleep(self.speed_rate)
        self.socket.wait(self.wait_rate)

    def move_left(self):
        self.socket.emit('heartbeat', self.LEFT)
        sleep(self.speed_rate)
        self.socket.wait(self.wait_rate)

    def move_up(self):
        self.socket.emit('heartbeat', self.UP)
        sleep(self.speed_rate)
        self.socket.wait(self.wait_rate)

    def move_down(self):
        self.socket.emit('heartbeat', self.DOWN)
        sleep(self.speed_rate)
        self.socket.wait(self.wait_rate)

    def get_visible_surroundings(self):
        return {
            'cells': self.board.visible_cells,
            'food': self.board.visible_food,
            'mass': self.board.visible_mass,
        }

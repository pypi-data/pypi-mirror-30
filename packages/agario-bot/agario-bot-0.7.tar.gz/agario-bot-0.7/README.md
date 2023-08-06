## agario-python-bot

##### Lightweight client library for writing agario bots in Python

##### socketio server: https://gitlab.com/unidev/agario

##### installation: pip install agario-bot

#### Examples

###### Simplest cycle bot
```python
from agario_bot.bot import BotClient

b = BotClient('prettygoo', wait_rate=0.1)
surroundings = b.get_visible_surroundings()

while True:
    b.move_left()
    surroundings = b.get_visible_surroundings()
    print(surroundings['cells'])
    print(surroundings['food'])

    b.move_up()
    surroundings = b.get_visible_surroundings()
    print(surroundings['cells'])
    print(surroundings['food'])

    b.move_right()
    surroundings = b.get_visible_surroundings()
    print(surroundings['cells'])
    print(surroundings['food'])

    b.move_down()
    surroundings = b.get_visible_surroundings()
    print(surroundings['cells'])
    print(surroundings['food'])
```

###### Scary bot, just runs away from everyone one the gameboard
```python
from agario_bot.examples.scary_bot import run_scary_bot
run_scary_bot()
```

##### BotClient arguments
- float:speed_rate - time to execute movement, 1 - one second
- float:wait_rate - time to wait before server response on client emitted socket
- list:cells - players
- mass - will be removed
- string:host - default localhost (0.0.0.0 will not work on Windows, 127.0.0.1 is highly likely not to work as well)
- int:port - must be None for real server deployment

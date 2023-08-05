# basic example

```
from agario_bot.bot import BotClient
b = BotClient('botname', speed_rate=1)

b = BotClient('prettygoo', wait_rate=0.1)
surroundings = b.get_visible_surroundings()

while True:
    b.move_left()
    surroundings = b.get_visible_surroundings()
    print(surroundings['cells'])
    print(surroundings['food'])
    print(surroundings['mass'])
    b.move_up()
    surroundings = b.get_visible_surroundings()
    print(surroundings['cells'])
    print(surroundings['food'])
    print(surroundings['mass'])
    b.move_right()
    surroundings = b.get_visible_surroundings()
    print(surroundings['cells'])
    print(surroundings['food'])
    print(surroundings['mass'])
    b.move_down()
    surroundings = b.get_visible_surroundings()
    print(surroundings['cells'])
    print(surroundings['food'])
    print(surroundings['mass'])


```
# where
- speed_rate - time to execute movement, 1 - one second
- wait_rate - time to wait before server response on client emitted socket
- cells - players
- mass - will be removed
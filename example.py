import pokepy
import asyncio

your_window_name = "mGBA - 0.10.1" #replace 0.10.1 with your version

game = pokepy.Game("mGBA - 0.10.1")

#simple code that prompts you when it's your turn to play
@game.event
async def on_combat():
    print(game.json_info)
    user_input = await asyncio.wait_for(asyncio.get_event_loop().run_in_executor(None, input, 'What you do?'), timeout=None)
    if user_input == "run":
        game.escape()
    else:
        for p in range(1,5):
            if int(user_input) == p:
                game.attack(p)
game.run()
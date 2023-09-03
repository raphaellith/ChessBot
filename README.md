# ChessBot
A Python chess bot for determining optimal moves in a chess game. No neural networks are used to make this bot.

The bot is intended to be used for real-life human-versus-bot games, and is thus optimized for that purpose.


# Requirements

As shown in the ```requirements.txt``` file, this program makes use of the following modules: ```chess```, ```gTTS``` and ```pygame```.


# Algorithm

The bot operates by generating all possible legal moves, evaluating a confidence score for each move, and then outputting the top few moves. Given some board layout B, the confidence score of a move M is rated using the following procedure:

1. Set up a hypothetical board _b_ which is identical to the current board layout _B_.
2. Perform move _M_ on _b_.
3. On _b_, randomly choose and perform one of the enemy's legal moves.
4. Similarly, respond by randomly choosing and performing one of the bot's legal move on _b_.
5. Repeat steps 3 to 4 on _b_ a number of times. The resultant board layout is labelled _b'_.
6. By comparing _B_ and _b'_ in terms of the number of white/black pieces, generate a "goodness" value for _M_.
7. Repeat steps 1 to 6 a number of times. The confidence score of _M_ is the mean of all goodness values.

Note that
- In step 5, the number of times steps 3 to 4 are repeated can be customized by the user via a parameter called ```moves_ahead```.
- In step 7, the number of times steps 1 to 6 are repeated can be also be customized, via the ```cautiousness``` parameter.
- Depending on how much the bot values defense over attack, it may output different goodness values for the same move in step 6. This is adjusted via the ```defense_to_attack_ratio``` parameter.


# Typical usage

The program revolves around the ```ChessBot``` class. As shown below, we can create a ```ChessBot``` object, specifying parameters like ```moves_ahead```, ```cautiousness``` and the ```defense_to_attack_ratio```.

```
from ChessBot import ChessBot

bot = ChessBot(moves_ahead=5, cautiousness=600, defense_to_attack_ratio=7.5)
```

To run a bot demonstration in the console, we can write the following line:

```
bot.play(my_color_is_white=False)
```

(```my_color_is_white``` is set to True if the bot takes the white side; and False otherwise.)

In the demonstration, every time the bot is asked to make a move, it determines and displays the top 5 optimal moves, in descending order of confidence. You may choose to accept the move (in which case the move will be performed), or to manually input a move yourself. In the case of the latter, use the following format when inputting the move:

```[source position]-[destination position]```

(for example: ```a1-a2```). Do not use algebraic chess notation. The same goes for when the enemy's move is to be inputted. Other important instructions will be displayed in the console during the demonstration.

If necessary, a read-aloud feature is provided for the demonstration. We can enable this feature by adding ```read_aloud=True``` as follows, in which case the best move (as decided by the bot) will be read out through a speaker or headphones.

```
bot.play(my_color_is_white=False, read_aloud=True)
```


# Possible future improvements

- Implement rollback for console inputs
- Implement a GUI to replace console interactions

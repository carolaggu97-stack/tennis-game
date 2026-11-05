# Tennis Game

A text-based tennis match in the terminal, written in Python. You play against the computer in a best-of-3-sets match, choosing your serve and your shots point by point, with real tennis scoring (15, 30, 40, deuce and advantage, games and sets).

## How to run

You need Python 3. No extra packages are needed.

```bash
python3 tennis_game.py
```

Each point, you choose a serve (flat or kick) and then a shot during the rally (forehand, backhand, lob or drop). Every shot has its own risk and reward: a flat serve or a drop shot can win the point outright, but is easier to miss.

## How it's built

- A `Player` class that works for both the human and the computer player
- A table of shot statistics (`power` and `fault_risk`) that decides each shot with a single random number
- Point, game, set and match logic, each layer built on the one below

The full write-up, with the design decisions and code explanations, is in [tennis_game_report.md](tennis_game_report.md).

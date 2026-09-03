# Python Terminal Tennis Game — Project Report

## Overview

This project is a fully interactive, text-based tennis simulator built in Python, playable directly in the terminal. A human player ("Alice") competes against a computer-controlled opponent in a best-of-3-set match, using authentic tennis scoring (points, games, sets, deuce, and advantage).

The game was built incrementally, layer by layer:

1. A `Player` class to represent each competitor
2. A shot-statistics table describing each shot's risk/reward
3. Point-by-point simulation, including serves and rallies
4. Game scoring (0 → 15 → 30 → 40 → win, with deuce/advantage)
5. Set scoring (first to 6 games, win by 2)
6. Match scoring (best of 3 sets)

Each layer builds directly on the one below it, mirroring how real tennis itself is structured.

---

## Design Decisions

Before writing any code, a few key decisions were made to scope the project:

| Decision | Choice | Reasoning |
|---|---|---|
| Player mode | Player vs. Computer | Easier to build, test, and debug solo before considering a two-player mode |
| Shot system | Real tennis shot names, with a choice each point | More engaging and strategic than a simple coin-flip |
| Scoring | Real tennis scoring (love/15/30/40, deuce, advantage, games, sets) | Chosen deliberately for realism over simplicity |
| Tiebreaks | Omitted | Kept the win condition simple (win by 2 games) to manage scope; noted as a natural extension |

---

## The `Player` Class

```python
class Player:
  def __init__(self, name, is_computer=False):
    self.name = name
    self.is_computer = is_computer
    self.points = 0
    self.games = 0
    self.sets = 0
```

Each `Player` object tracks its own name, whether it's computer-controlled, and its current points/games/sets — all of which reset and update as the match progresses.

**Key design choice — `is_computer` as a flag, not a separate class:** rather than writing a separate `ComputerPlayer` class, a single `Player` class handles both humans and the AI, branching internally based on `is_computer`. This keeps the rest of the game's logic (`play_point`, `play_game`, etc.) completely agnostic to *who* is making a choice — it just calls `player.choose_shot()` and lets the object figure out whether that means prompting a human via `input()` or picking randomly.

```python
def choose_shot(self):
  options = ["forehand", "backhand", "lob", "drop"]
  if self.is_computer:
    return random.choice(options)
  else:
    choice = input("...").strip().lower()
    mapping = {"f": "forehand", "b": "backhand", "l": "lob", "d": "drop"}
    return mapping.get(choice, "forehand")
```

A `__repr__()` method was also added so that printing a `Player` object (e.g., during debugging) shows a clean summary instead of a default memory address:

```
Player('Alice', 1 sets, 3 games, 2 points)
```

---

## Shot Statistics

Every shot in the game — two serve types and four rally shots — has two associated numbers, stored in the `SHOT_STATS` dictionary:

- **`power`** — the probability that this shot wins the point outright (an unreturnable winner)
- **`fault_risk`** — the probability that this shot fails (into the net, or out)

```python
SHOT_STATS = {
  "flat_serve": {"power": 0.35, "fault_risk": 0.25},
  "kick_serve": {"power": 0.15, "fault_risk": 0.10},
  "forehand":   {"power": 0.25, "fault_risk": 0.15},
  "backhand":   {"power": 0.20, "fault_risk": 0.18},
  "lob":        {"power": 0.05, "fault_risk": 0.05},
  "drop":       {"power": 0.30, "fault_risk": 0.30},
}
```

This models the real tradeoffs found in tennis strategy:

- **Flat serve** — high power, but risky (mirrors an aggressive, fast first serve)
- **Kick serve** — safer, more consistent, less powerful (a common "safe second serve")
- **Forehand** — a balanced, reliable shot most players lean on
- **Backhand** — slightly less powerful and slightly riskier, reflecting that many players' backhand is their weaker side
- **Lob** — very low risk, very low reward — a defensive, rally-extending shot
- **Drop shot** — high risk, high reward — capable of winning outright, but easy to mishit

This dictionary is defined once, outside any class, since it represents shared, fixed game data rather than something that varies per player.

---

## Point Logic — `attempt_serve()` and `play_point()`

### Serving and double faults

```python
def attempt_serve(server):
  serve_choice = server.choose_serve()
  serve_key = serve_choice + "_serve"
  stats = SHOT_STATS[serve_key]
  roll = random.random()
  if roll < stats["fault_risk"]:
    return False  # fault
  return True  # serve is in
```

Real tennis gives a server **two chances** to land a serve — a second attempt only if the first faults, and losing the point automatically ("double fault") if both fail. This is implemented directly in `play_point()`:

```python
if not attempt_serve(server):
  print("First serve fault!")
  if not attempt_serve(server):
    print("Double fault! Point goes to {}.".format(returner.name))
    return returner
```

### The rally

Once a serve is in, the point becomes a rally: players alternate hitting shots until either a fault occurs, a winner is hit, or (as a safeguard) the rally exceeds 10 exchanges, at which point the point is awarded randomly to prevent any theoretical infinite loop.

```python
current_hitter = returner
other = server

for shot_number in range(10):
  shot = current_hitter.choose_shot()
  stats = SHOT_STATS[shot]
  roll = random.random()

  if roll < stats["fault_risk"]:
    return other          # the hitter faulted; opponent wins the point

  if roll < stats["fault_risk"] + stats["power"]:
    return current_hitter  # the hitter won outright

  current_hitter, other = other, current_hitter  # rally continues
```

**How the random roll is interpreted:**

- `roll < fault_risk` → the shot fails (unforced error)
- `fault_risk ≤ roll < fault_risk + power` → the shot is a clean winner
- Otherwise → the shot lands safely in play, and the rally continues with the opponent hitting next

This single comparison elegantly captures three outcomes from one random number, weighted by each shot's own risk/reward profile.

---

## Game Scoring — `play_game()`

Real tennis scoring doesn't count points as 1, 2, 3 — it uses 0, 15, 30, 40, then "game," with a special *deuce/advantage* system once both players are tied at 40. Internally, points are tracked as plain integers (0, 1, 2, 3...) and only converted to their traditional display names when printed:

```python
POINT_NAMES = ["0", "15", "30", "40"]

def score_display(p1, p2):
  if p1.points >= 3 and p2.points >= 3:
    if p1.points == p2.points:
      return "Deuce"
    elif p1.points > p2.points:
      return "Advantage {}".format(p1.name)
    else:
      return "Advantage {}".format(p2.name)
  return "{} - {}".format(POINT_NAMES[p1.points], POINT_NAMES[p2.points])
```

The win condition for a game is a single, elegant rule that naturally handles both the normal case and deuce:

```python
if winner.points >= 4 and winner.points - loser_points(...) >= 2:
  winner.games += 1
  return winner
```

**Why this one condition covers everything:** a player needs at least 4 points to win *and* a 2-point lead. In a normal game, this resolves quickly (4-0, 4-1, 4-2). Once a game reaches deuce (3-3, i.e., 40-40), this same rule keeps the game going until someone pulls 2 points ahead — correctly producing scores like 5-3, 6-4, or even longer deuce battles, exactly matching real tennis rules, without needing separate logic for the deuce case.

---

## Set Scoring — `play_set()`

A set is a sequence of games, won by whoever first reaches 6 games with at least a 2-game lead (tiebreaks were intentionally omitted to keep scope manageable):

```python
def play_set(player1, player2):
  server, returner = player1, player2
  while True:
    play_game(server, returner)
    if player1.games >= 6 and player1.games - player2.games >= 2:
      player1.sets += 1
      return player1
    if player2.games >= 6 and player2.games - player1.games >= 2:
      player2.sets += 1
      return player2
    server, returner = returner, server  # serve alternates each game
```

**A key realism detail:** real tennis alternates who serves every single game, regardless of who won the previous one. This is handled with a simple variable swap, `server, returner = returner, server`, at the end of every game loop — a small line doing a lot of realism work.

---

## Match Scoring — `play_match()`

The outermost layer: a match is simply "first to win 2 sets" (best of 3):

```python
def play_match(player1, player2):
  while True:
    play_set(player1, player2)
    if player1.sets == 2:
      return player1
    if player2.sets == 2:
      return player2
```

This function ties every layer together — points feed into games, games feed into sets, and sets feed into the match — mirroring tennis's real nested scoring structure from the ground up.

---

## Architecture Summary

```
play_match()
  └── play_set()          [repeats until a player reaches 2 sets]
        └── play_game()   [repeats until a player reaches 6 games, win by 2]
              └── play_point()   [repeats until a player reaches 4 points, win by 2]
                    ├── attempt_serve()   [up to 2 tries; double fault if both fail]
                    └── rally loop        [alternates shots until fault/winner]
```

Each layer is a `while True:` loop that repeatedly calls the layer below it, checking a win condition after each call — a clean, recursive-feeling structure without actual recursion, and one that closely mirrors how a real tennis match is verbally described: "first to 4 points wins a game, first to 6 games wins a set, first to 2 sets wins the match."

---

## What Was Tested

The finished game was played through a complete, real match from start to finish, exercising every piece of logic along the way:

- Multiple full games, including several that reached deuce and required multiple advantage swings before resolving
- At least one double fault
- Multiple first-serve faults followed by successful second serves
- A full set that went to 7-5
- A second full set that went to 8-6
- A deciding third set
- Serve correctly alternating every single game
- Score correctly resetting between games and between sets
- A clean, correct match-ending condition once a player reached 2 sets

The match concluded with a final score of **Computer defeating Alice, 2 sets to 1** (7-5, 6-8, 3-6), with every score, fault, and win message printing accurately throughout.

---

## Possible Extensions

Ideas for building on this project further:

- **Tiebreaks** — implement the real tiebreak rule for 6-6 set scores, rather than requiring a 2-game lead indefinitely
- **Two-player mode** — allow two humans to play, alternating `input()` prompts by whose turn it is
- **Difficulty levels** — give the computer player its own tunable stats, rather than pure randomness
- **Match statistics** — track and display stats at the end (aces, double faults, winners, unforced errors)
- **Best-of-5 option** — extend `play_match()`'s win condition to support a configurable number of sets

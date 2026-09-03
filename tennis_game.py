import random
SHOT_STATS = {
  "flat_serve": {"power": 0.35, "fault_risk": 0.25},
  "kick_serve": {"power": 0.15, "fault_risk": 0.10},
  "forehand":   {"power": 0.25, "fault_risk": 0.15},
  "backhand":   {"power": 0.20, "fault_risk": 0.18},
  "lob":        {"power": 0.05, "fault_risk": 0.05},
  "drop":       {"power": 0.30, "fault_risk": 0.30},
}
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
class Player:
  def __init__(self, name, is_computer=False):
    self.name = name
    self.is_computer = is_computer
    self.points = 0     # 0, 15, 30, 40 (we'll represent as 0,1,2,3 internally)
    self.games = 0
    self.sets = 0

  def choose_serve(self):
    if self.is_computer:
      return random.choice(["flat", "kick"])
    else:
      choice = input("{}, choose your serve - (F)lat or (K)ick: ".format(self.name)).strip().lower()
      return "flat" if choice.startswith("f") else "kick"

  def choose_shot(self):
    options = ["forehand", "backhand", "lob", "drop"]
    if self.is_computer:
      return random.choice(options)
    else:
      choice = input("{}, choose your shot - (F)orehand, (B)ackhand, (L)ob, (D)rop: ".format(self.name)).strip().lower()
      mapping = {"f": "forehand", "b": "backhand", "l": "lob", "d": "drop"}
      return mapping.get(choice, "forehand")

  def __repr__(self):
    return "Player('{}', {} sets, {} games, {} points)".format(
      self.name, self.sets, self.games, self.points)

def attempt_serve(server):
  serve_choice = server.choose_serve()
  serve_key = serve_choice + "_serve"
  stats = SHOT_STATS[serve_key]
  roll = random.random()
  if roll < stats["fault_risk"]:
    return False  # fault
  return True  # serve is in

def play_point(server, returner):
  # First serve attempt
  print("\n{} is serving...".format(server.name))
  if not attempt_serve(server):
    print("First serve fault!")
    # Second serve attempt
    if not attempt_serve(server):
      print("Double fault! Point goes to {}.".format(returner.name))
      return returner

  print("Serve is in! Rally begins.")

  # Simple rally: each player picks a shot, we compare outcomes
  current_hitter = returner
  other = server

  for shot_number in range(10):  # cap rally length so it doesn't go forever
    shot = current_hitter.choose_shot()
    stats = SHOT_STATS[shot]
    roll = random.random()

    if roll < stats["fault_risk"]:
      print("{} hits a {} into the net/out! Point to {}.".format(current_hitter.name, shot, other.name))
      return other

    if roll < stats["fault_risk"] + stats["power"]:
      print("{} hits a winning {}! Point to {}.".format(current_hitter.name, shot, current_hitter.name))
      return current_hitter

    print("{} returns with a {}.".format(current_hitter.name, shot))
    current_hitter, other = other, current_hitter

  # If rally goes too long, randomly award the point
  print("Long rally! Point goes to a random player.")
  return random.choice([server, returner])
def loser_points(winner, server, returner):
  return returner.points if winner is server else server.points

def play_game(server, returner):
  server.points = 0
  returner.points = 0

  print("\n=== New Game: {} serving ===".format(server.name))

  while True:
    print("Score: {}".format(score_display(server, returner)))
    winner = play_point(server, returner)
    winner.points += 1

    if winner.points >= 4 and winner.points - loser_points(winner, server, returner) >= 2:
      print("\nGame won by {}!".format(winner.name))
      winner.games += 1
      return winner
def play_set(player1, player2):
  player1.games = 0
  player2.games = 0

  print("\n########## New Set ##########")

  server, returner = player1, player2

  while True:
    winner = play_game(server, returner)

    print("Games — {}: {}, {}: {}".format(player1.name, player1.games, player2.name, player2.games))

    if player1.games >= 6 and player1.games - player2.games >= 2:
      print("\nSet won by {}!".format(player1.name))
      player1.sets += 1
      return player1
    if player2.games >= 6 and player2.games - player1.games >= 2:
      print("\nSet won by {}!".format(player2.name))
      player2.sets += 1
      return player2

    server, returner = returner, server


def play_match(player1, player2):
  print("\n@@@@@@@@@@ MATCH START: {} vs {} @@@@@@@@@@".format(player1.name, player2.name))

  while True:
    winner = play_set(player1, player2)

    print("Sets — {}: {}, {}: {}".format(player1.name, player1.sets, player2.name, player2.sets))

    if player1.sets == 2:
      print("\n🏆 {} WINS THE MATCH! 🏆".format(player1.name))
      return player1
    if player2.sets == 2:
      print("\n🏆 {} WINS THE MATCH! 🏆".format(player2.name))
      return player2
    
if __name__ == "__main__":
  p1 = Player("Alice")
  p2 = Player("Computer", is_computer=True)

  play_match(p1, p2)
class Player {
  final String name;
  int runs = 0;
  int ballsFaced = 0;
  int fours = 0;
  int sixes = 0;
  int wickets = 0;
  int ballsBowled = 0;
  int runsConceded = 0;
  int dotBalls = 0;

  Player({required this.name});

  // Calculate strike rate
  double get strikeRate => ballsFaced == 0 ? 0 : (runs / ballsFaced) * 100;

  // Calculate bowling economy
  double get economyRate => ballsBowled == 0 ? 0 : (runsConceded / ballsBowled) * 6;
}

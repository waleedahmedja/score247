class Player {
  final String name; // Player's name
  int runs = 0; // Total runs scored
  int ballsFaced = 0; // Balls faced by the player
  int fours = 0; // Number of fours hit
  int sixes = 0; // Number of sixes hit
  int wickets = 0; // Number of wickets taken
  int ballsBowled = 0; // Balls bowled by the player
  int runsConceded = 0; // Runs conceded while bowling
  int dotBalls = 0; // Number of dot balls bowled

  // Constructor
  Player({required this.name});

  /// Calculate batting strike rate.
  /// Returns 0 if no balls faced.
  double get strikeRate => ballsFaced == 0 ? 0 : (runs / ballsFaced) * 100;

  /// Calculate bowling economy rate.
  /// Returns 0 if no balls bowled.
  double get economyRate => ballsBowled == 0 ? 0 : (runsConceded / ballsBowled) * 6;

  /// Increment runs scored by the player.
  /// Updates runs, balls faced, and boundary counts accordingly.
  void addRuns(int additionalRuns) {
    runs += additionalRuns;
    ballsFaced++;

    // Update boundary counts
    if (additionalRuns == 4) fours++;
    if (additionalRuns == 6) sixes++;
  }

  /// Increment dot balls faced or bowled.
  void addDotBall() {
    dotBalls++;
    ballsFaced++;
  }

  /// Increment bowling stats.
  /// Updates runs conceded and balls bowled.
  void addBowlingStats(int runsGiven, {bool isDotBall = false}) {
    runsConceded += runsGiven;
    ballsBowled++;
    if (isDotBall) dotBalls++;
  }

  /// Increment wickets taken by the player.
  void addWicket() {
    wickets++;
  }

  /// Reset all player stats (for a new match or innings).
  void resetStats() {
    runs = 0;
    ballsFaced = 0;
    fours = 0;
    sixes = 0;
    wickets = 0;
    ballsBowled = 0;
    runsConceded = 0;
    dotBalls = 0;
  }
}

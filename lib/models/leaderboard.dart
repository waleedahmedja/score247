class Leaderboard {
  List<Player> players;

  Leaderboard(this.players);

  // Sort players by runs scored
  List<Player> get topRunScorers {
    players.sort((a, b) => b.runs.compareTo(a.runs));
    return players;
  }

  // Sort bowlers by wickets taken
  List<Player> get topBowlers {
    players.sort((a, b) => b.wickets.compareTo(a.wickets));
    return players;
  }
}

import 'player.dart'; // Ensure this is the correct import path for the Player model.

class Leaderboard {
  final List<Player> players;

  Leaderboard(this.players);

  /// Get top run scorers.
  /// Returns a list of players sorted by runs scored in descending order.
  List<Player> get topRunScorers {
    // Return a sorted copy of the list by runs
    return List.from(players)
      ..sort((a, b) => b.runs.compareTo(a.runs));
  }

  /// Get top bowlers.
  /// Returns a list of players sorted by wickets taken in descending order.
  List<Player> get topBowlers {
    // Return a sorted copy of the list by wickets
    return List.from(players)
      ..sort((a, b) => b.wickets.compareTo(a.wickets));
  }

  /// Get top players based on runs (limited to `count`).
  List<Player> getTopRunScorers({int count = 5}) {
    final sortedPlayers = topRunScorers;
    return sortedPlayers.take(count).toList();
  }

  /// Get top players based on wickets (limited to `count`).
  List<Player> getTopBowlers({int count = 5}) {
    final sortedPlayers = topBowlers;
    return sortedPlayers.take(count).toList();
  }
}

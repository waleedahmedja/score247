import 'package:flutter/material.dart';
import '../models/player.dart';
import '../models/leaderboard.dart';

class LeaderboardScreen extends StatelessWidget {
  final List<Player> players;

  const LeaderboardScreen({super.key, required this.players});

  @override
  Widget build(BuildContext context) {
    final leaderboard = Leaderboard(players);

    return Scaffold(
      appBar: AppBar(title: const Text("Leaderboard")),
      backgroundColor: Colors.grey[900],
      body: ListView(
        children: [
          const Text(
            "Top Run Scorers",
            style: TextStyle(color: Colors.white, fontSize: 20),
          ),
          ...leaderboard.topRunScorers.map((player) => ListTile(
                title: Text(player.name, style: const TextStyle(color: Colors.white)),
                subtitle: Text("Runs: ${player.runs}", style: const TextStyle(color: Colors.white70)),
              )),
          const SizedBox(height: 20),
          const Text(
            "Top Bowlers",
            style: TextStyle(color: Colors.white, fontSize: 20),
          ),
          ...leaderboard.topBowlers.map((player) => ListTile(
                title: Text(player.name, style: const TextStyle(color: Colors.white)),
                subtitle: Text("Wickets: ${player.wickets}", style: const TextStyle(color: Colors.white70)),
              )),
        ],
      ),
    );
  }
}

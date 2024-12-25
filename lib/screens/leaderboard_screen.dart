// leaderboard_screen.dart
import 'package:flutter/material.dart';
import '../models/player.dart';

class LeaderboardScreen extends StatelessWidget {
  final List<Player> players;

  const LeaderboardScreen({super.key, required this.players});

  @override
  Widget build(BuildContext context) {
    // Sort players for leaderboard
    players.sort((a, b) => b.runs.compareTo(a.runs)); // By runs scored

    return Scaffold(
      appBar: AppBar(
        title: const Text("Leaderboard"),
        backgroundColor: Colors.blueAccent,
      ),
      backgroundColor: Colors.grey[900],
      body: ListView.builder(
        itemCount: players.length,
        itemBuilder: (context, index) {
          final player = players[index];
          return ListTile(
            title: Text(
              "${index + 1}. ${player.name}",
              style: const TextStyle(color: Colors.white),
            ),
            subtitle: Text(
              "Runs: ${player.runs}, Wickets: ${player.wickets}",
              style: const TextStyle(color: Colors.white70),
            ),
          );
        },
      ),
    );
  }
}

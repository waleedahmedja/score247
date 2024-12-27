import 'package:flutter/material.dart';
import '../models/player.dart';

class LeaderboardScreen extends StatefulWidget {
  final List<Player> players;

  const LeaderboardScreen({super.key, required this.players});

  @override
  _LeaderboardScreenState createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen> {
  // Current sorting criteria: 'runs' or 'wickets'
  String _currentCriteria = 'runs';

  @override
  Widget build(BuildContext context) {
    // Create a sorted copy of the players list
    final List<Player> sortedPlayers = List.from(widget.players)
      ..sort((a, b) {
        if (_currentCriteria == 'runs') {
          return b.runs.compareTo(a.runs); // Sort by runs scored
        } else {
          return b.wickets.compareTo(a.wickets); // Sort by wickets taken
        }
      });

    return Scaffold(
      appBar: AppBar(
        title: const Text("Leaderboard"),
        backgroundColor: Colors.blueAccent,
      ),
      backgroundColor: Colors.grey[900],
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Sorting Toggle
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  "Sort by:",
                  style: TextStyle(color: Colors.white, fontSize: 16),
                ),
                DropdownButton<String>(
                  value: _currentCriteria,
                  dropdownColor: Colors.grey[800],
                  style: const TextStyle(color: Colors.white),
                  items: const [
                    DropdownMenuItem(
                      value: 'runs',
                      child: Text("Runs"),
                    ),
                    DropdownMenuItem(
                      value: 'wickets',
                      child: Text("Wickets"),
                    ),
                  ],
                  onChanged: (value) {
                    setState(() {
                      _currentCriteria = value!;
                    });
                  },
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Leaderboard List
            Expanded(
              child: sortedPlayers.isEmpty
                  ? const Center(
                      child: Text(
                        "No players to display.",
                        style: TextStyle(color: Colors.white70, fontSize: 16),
                      ),
                    )
                  : ListView.builder(
                      itemCount: sortedPlayers.length,
                      itemBuilder: (context, index) {
                        final player = sortedPlayers[index];
                        return ListTile(
                          leading: CircleAvatar(
                            backgroundColor: Colors.blueAccent,
                            child: Text(
                              "${index + 1}",
                              style: const TextStyle(color: Colors.white),
                            ),
                          ),
                          title: Text(
                            player.name,
                            style: const TextStyle(color: Colors.white),
                          ),
                          subtitle: Text(
                            _currentCriteria == 'runs'
                                ? "Runs: ${player.runs}"
                                : "Wickets: ${player.wickets}",
                            style: const TextStyle(color: Colors.white70),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

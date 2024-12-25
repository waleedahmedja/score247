import 'package:flutter/material.dart';

class TossScreen extends StatelessWidget {
  final int selectedPlayers;
  final String selectedOvers;
  final String selectedToss;

  const TossScreen({
    super.key,
    required this.selectedPlayers,
    required this.selectedOvers,
    required this.selectedToss,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: const Text("Toss Animation"),
        backgroundColor: Colors.blueAccent,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              "Tossing the coin...",
              style: TextStyle(color: Colors.white, fontSize: 20),
            ),
            const SizedBox(height: 20),
            // Placeholder for coin animation
            const CircularProgressIndicator(color: Colors.blueAccent),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // Randomly select winner
                final tossResult =
                    (selectedToss == "Heads" ? "Team 1" : "Team 2");
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('$tossResult won the toss!')),
                );
                // TODO: Navigate to the match screen
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
              ),
              child: const Text("Next"),
            ),
          ],
        ),
      ),
    );
  }
}
class TossScreen extends StatelessWidget {
  final String team1Name;
  final String team2Name;
  final int oversPerMatch;

  const TossScreen({
    super.key,
    required this.team1Name,
    required this.team2Name,
    required this.oversPerMatch,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: const Text("Toss"),
        backgroundColor: Colors.blueAccent,
      ),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => MatchScreen(
                  team1Name: team1Name,
                  team2Name: team2Name,
                  oversPerMatch: oversPerMatch,
                ),
              ),
            );
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green,
            padding: const EdgeInsets.symmetric(vertical: 16),
          ),
          child: const Text(
            "Start Match",
            style: TextStyle(fontSize: 18),
          ),
        ),
      ),
    );
  }
}

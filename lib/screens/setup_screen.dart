import 'package:flutter/material.dart';
import 'settings_screen.dart'; // Import the new settings screen

class SetupScreen extends StatefulWidget {
  const SetupScreen({super.key});

  @override
  _SetupScreenState createState() => _SetupScreenState();
}

class _SetupScreenState extends State<SetupScreen> {
  String team1Name = "Team 1";
  String team2Name = "Team 2";
  int oversPerMatch = 20; // Default number of overs

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: const Text("Match Setup"),
        backgroundColor: Colors.blueAccent,
        actions: [
          // Navigate to Settings Screen
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () async {
              final result = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const SettingsScreen(),
                ),
              );

              if (result != null) {
                setState(() {
                  oversPerMatch = result;
                });
              }
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Existing setup fields (Team Names, Match Type, etc.)
            const Text(
              "Team Names:",
              style: TextStyle(color: Colors.white, fontSize: 16),
            ),
            TextField(
              onChanged: (value) => setState(() => team1Name = value),
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: "Enter Team 1 Name",
                filled: true,
                fillColor: Colors.grey[800],
                hintStyle: const TextStyle(color: Colors.white60),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
            ),
            const SizedBox(height: 20),
            TextField(
              onChanged: (value) => setState(() => team2Name = value),
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: "Enter Team 2 Name",
                filled: true,
                fillColor: Colors.grey[800],
                hintStyle: const TextStyle(color: Colors.white60),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Display overs per match
            Text(
              "Overs per Match: $oversPerMatch",
              style: const TextStyle(color: Colors.white, fontSize: 16),
            ),
            const SizedBox(height: 20),

            ElevatedButton(
              onPressed: () {
                // Proceed to match screen
              },
              child: const Text("Start Match"),
            ),
          ],
        ),
      ),
    );
  }
}

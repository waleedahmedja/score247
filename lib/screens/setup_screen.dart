import 'package:flutter/material.dart';
import 'match_screen.dart';
import 'quick_match_screen.dart';

class SetupScreen extends StatefulWidget {
  const SetupScreen({super.key});

  @override
  _SetupScreenState createState() => _SetupScreenState();
}

class _SetupScreenState extends State<SetupScreen> {
  String team1Name = "Team 1";
  String team2Name = "Team 2";
  List<String> team1Players = [];
  List<String> team2Players = [];
  String matchMode = "Quick Match";

  final List<String> matchModes = ["Quick Match", "Advanced Match"];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: const Text('Match Setup'),
        backgroundColor: Colors.blueAccent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Team 1 Name
            const Text("Team 1 Name:", style: TextStyle(color: Colors.white)),
            const SizedBox(height: 8),
            TextField(
              onChanged: (value) => setState(() => team1Name = value),
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.grey[800],
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                hintText: "Enter Team 1 Name",
                hintStyle: const TextStyle(color: Colors.white60),
              ),
            ),
            const SizedBox(height: 20),

            // Team 2 Name
            const Text("Team 2 Name:", style: TextStyle(color: Colors.white)),
            const SizedBox(height: 8),
            TextField(
              onChanged: (value) => setState(() => team2Name = value),
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.grey[800],
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                hintText: "Enter Team 2 Name",
                hintStyle: const TextStyle(color: Colors.white60),
              ),
            ),
            const SizedBox(height: 20),

            // Match Mode Selector
            const Text("Match Mode:", style: TextStyle(color: Colors.white)),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: matchMode,
              onChanged: (value) => setState(() => matchMode = value!),
              items: matchModes
                  .map((mode) => DropdownMenuItem(value: mode, child: Text(mode)))
                  .toList(),
              dropdownColor: Colors.grey[800],
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.grey[800],
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
            const SizedBox(height: 30),

            // Proceed Button
            ElevatedButton(
              onPressed: () {
                if (matchMode == "Quick Match") {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => QuickMatchScreen(
                        team1Name: team1Name,
                        team2Name: team2Name,
                      ),
                    ),
                  );
                } else {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => MatchScreen(
                        team1Name: team1Name,
                        team2Name: team2Name,
                        team1Players: team1Players,
                        team2Players: team2Players,
                      ),
                    ),
                  );
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text("Start Match", style: TextStyle(fontSize: 18)),
            ),
          ],
        ),
      ),
    );
  }
}

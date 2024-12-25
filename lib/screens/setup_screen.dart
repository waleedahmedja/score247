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

class SetupScreen extends StatefulWidget {
  const SetupScreen({super.key});

  @override
  _SetupScreenState createState() => _SetupScreenState();
}

class _SetupScreenState extends State<SetupScreen> {
  String team1Name = "";
  String team2Name = "";
  int oversPerMatch = 20;

  void validateAndNavigate() {
    if (team1Name.isEmpty || team2Name.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please enter team names!")),
      );
    } else {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => TossScreen(
            team1Name: team1Name,
            team2Name: team2Name,
            oversPerMatch: oversPerMatch,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: const Text("Match Setup"),
        backgroundColor: Colors.blueAccent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Team 1 Input
            const Text("Team 1 Name:", style: TextStyle(color: Colors.white)),
            const SizedBox(height: 8),
            TextField(
              onChanged: (value) => setState(() => team1Name = value),
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.grey[800],
                border:
                    OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                hintText: "Enter Team 1 Name",
                hintStyle: const TextStyle(color: Colors.white60),
              ),
            ),
            const SizedBox(height: 20),

            // Team 2 Input
            const Text("Team 2 Name:", style: TextStyle(color: Colors.white)),
            const SizedBox(height: 8),
            TextField(
              onChanged: (value) => setState(() => team2Name = value),
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.grey[800],
                border:
                    OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                hintText: "Enter Team 2 Name",
                hintStyle: const TextStyle(color: Colors.white60),
              ),
            ),
            const SizedBox(height: 20),

            // Overs Per Match Display
            Text(
              "Overs per Match: $oversPerMatch",
              style: const TextStyle(color: Colors.white, fontSize: 16),
            ),
            const SizedBox(height: 20),

            // Navigate to Toss Screen
            ElevatedButton(
              onPressed: validateAndNavigate,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text(
                "Proceed to Toss",
                style: TextStyle(fontSize: 18),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
ElevatedButton(
  onPressed: () {
    Navigator.pushNamed(
      context,
      '/toss',
      arguments: {
        'team1Name': team1Name,
        'team2Name': team2Name,
        'oversPerMatch': oversPerMatch,
      },
    );
  },
  child: const Text("Proceed to Toss"),
),
void validateInputs() {
  if (team1Name.isEmpty || team2Name.isEmpty) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("Team names cannot be empty!"),
      ),
    );
  } else {
    Navigator.pushNamed(context, '/toss', arguments: {
      'team1Name': team1Name,
      'team2Name': team2Name,
      'oversPerMatch': oversPerMatch,
    });
  }
}
ElevatedButton(
  onPressed: validateInputs,
  child: const Text("Proceed to Toss"),
),
TextField(
  onChanged: (value) {
    setState(() {
      team1Name = value;
    });
  },
  decoration: InputDecoration(
    labelText: 'Enter Team 1 Name',
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
  ),
),
TextField(
  onChanged: (value) {
    setState(() {
      team2Name = value;
    });
  },
  decoration: InputDecoration(
    labelText: 'Enter Team 2 Name',
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
  ),
),

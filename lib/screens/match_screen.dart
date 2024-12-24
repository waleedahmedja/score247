import 'package:flutter/material.dart';

class MatchScreen extends StatefulWidget {
  final int playersPerTeam;
  final String overs;
  final String tossWinner;

  const MatchScreen({
    super.key,
    required this.playersPerTeam,
    required this.overs,
    required this.tossWinner,
  });

  @override
  _MatchScreenState createState() => _MatchScreenState();
}

class _MatchScreenState extends State<MatchScreen> {
  // Match state
  int team1Runs = 0;
  int team1Wickets = 0;
  int team1Balls = 0;

  int team2Runs = 0;
  int team2Wickets = 0;
  int team2Balls = 0;

  bool isTeam1Batting = true;
  late int totalBalls; // Total balls per innings (overs * 6)

  @override
  void initState() {
    super.initState();
    // Calculate total balls for an innings
    totalBalls = widget.overs == "Unlimited"
        ? 9999 // Practically unlimited
        : int.parse(widget.overs) * 6;
  }

  // Handle score update
  void updateScore(int runs, {bool isWicket = false, bool isExtraBall = false}) {
    setState(() {
      if (isTeam1Batting) {
        // Team 1 is batting
        if (isWicket) {
          team1Wickets++;
        } else {
          team1Runs += runs;
        }
        if (!isExtraBall) team1Balls++;
      } else {
        // Team 2 is batting
        if (isWicket) {
          team2Wickets++;
        } else {
          team2Runs += runs;
        }
        if (!isExtraBall) team2Balls++;
      }

      // Check for innings end conditions
      checkInningsEnd();
    });
  }

  // Check if innings has ended
  void checkInningsEnd() {
    final currentBalls = isTeam1Batting ? team1Balls : team2Balls;
    final currentWickets = isTeam1Batting ? team1Wickets : team2Wickets;

    if (currentBalls >= totalBalls || currentWickets >= widget.playersPerTeam - 1) {
      // End the current innings
      if (isTeam1Batting) {
        setState(() {
          isTeam1Batting = false;
        });
      } else {
        // Match ends after Team 2's innings
        showMatchSummary();
      }
    }
  }

  // Show match summary
  void showMatchSummary() {
    String result;
    if (team1Runs > team2Runs) {
      result = "Team 1 wins by ${team1Runs - team2Runs} runs!";
    } else if (team2Runs > team1Runs) {
      result = "Team 2 wins by ${widget.playersPerTeam - 1 - team2Wickets} wickets!";
    } else {
      result = "It's a tie!";
    }

    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Match Summary"),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text("Team 1: $team1Runs/${team1Wickets}"),
            Text("Team 2: $team2Runs/${team2Wickets}"),
            const SizedBox(height: 20),
            Text(result),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context); // Go back to setup screen
            },
            child: const Text("Back to Setup"),
          ),
        ],
      ),
    );
  }

  // Reset for next innings
  void nextInnings() {
    setState(() {
      isTeam1Batting = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final currentRuns = isTeam1Batting ? team1Runs : team2Runs;
    final currentWickets = isTeam1Batting ? team1Wickets : team2Wickets;
    final currentBalls = isTeam1Batting ? team1Balls : team2Balls;

    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: Text(isTeam1Batting ? "Team 1 Batting" : "Team 2 Batting"),
        backgroundColor: Colors.blueAccent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // Scorecard
            Column(
              children: [
                Text(
                  "$currentRuns/$currentWickets",
                  style: const TextStyle(color: Colors.white, fontSize: 40),
                ),
                const SizedBox(height: 10),
                Text(
                  "Overs: ${currentBalls ~/ 6}.${currentBalls % 6}",
                  style: const TextStyle(color: Colors.white, fontSize: 20),
                ),
              ],
            ),

            // Control Buttons
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                ElevatedButton(
                  onPressed: () => updateScore(1),
                  child: const Text("One"),
                ),
                ElevatedButton(
                  onPressed: () => updateScore(2),
                  child: const Text("Two"),
                ),
                ElevatedButton(
                  onPressed: () => updateScore(3),
                  child: const Text("Three"),
                ),
                ElevatedButton(
                  onPressed: () => updateScore(4),
                  child: const Text("Four"),
                ),
                ElevatedButton(
                  onPressed: () => updateScore(6),
                  child: const Text("Six"),
                ),
                ElevatedButton(
                  onPressed: () => updateScore(0, isWicket: true),
                  child: const Text("Wicket"),
                ),
                ElevatedButton(
                  onPressed: () => updateScore(1, isExtraBall: true),
                  child: const Text("Wide"),
                ),
                ElevatedButton(
                  onPressed: () => updateScore(1, isExtraBall: true),
                  child: const Text("No Ball"),
                ),
                ElevatedButton(
                  onPressed: () => updateScore(0, isExtraBall: true),
                  child: const Text("Ball Again"),
                ),
              ],
            ),

            // Next Innings or End Match Button
            if (isTeam1Batting)
              ElevatedButton(
                onPressed: nextInnings,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text("Next Innings"),
              ),
          ],
        ),
      ),
    );
  }
}

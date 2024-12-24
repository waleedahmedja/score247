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
  int team1Runs = 0;
  int team1Wickets = 0;
  int team1Balls = 0;

  int team2Runs = 0;
  int team2Wickets = 0;
  int team2Balls = 0;

  bool isTeam1Batting = true;
  late int totalBalls;

  @override
  void initState() {
    super.initState();
    totalBalls = widget.overs == "Unlimited" ? 9999 : int.parse(widget.overs) * 6;
  }

  void updateScore(int runs, {bool isWicket = false, bool isExtraBall = false}) {
    setState(() {
      if (isTeam1Batting) {
        if (isWicket) {
          team1Wickets++;
        } else {
          team1Runs += runs;
        }
        if (!isExtraBall) team1Balls++;
      } else {
        if (isWicket) {
          team2Wickets++;
        } else {
          team2Runs += runs;
        }
        if (!isExtraBall) team2Balls++;
      }

      checkInningsEnd();
    });
  }

  void checkInningsEnd() {
    final currentBalls = isTeam1Batting ? team1Balls : team2Balls;
    final currentWickets = isTeam1Batting ? team1Wickets : team2Wickets;

    if (currentBalls >= totalBalls || currentWickets >= widget.playersPerTeam - 1) {
      if (isTeam1Batting) {
        setState(() {
          isTeam1Batting = false;
        });
      } else {
        showMatchSummary();
      }
    }
  }

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
          children: [
            // Scorecard Display
            Card(
              color: Colors.grey[800],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              elevation: 5,
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  children: [
                    Text(
                      "$currentRuns/$currentWickets",
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 40,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      "Overs: ${currentBalls ~/ 6}.${currentBalls % 6}",
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 20,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Buttons for Scoring
            Expanded(
              child: GridView.count(
                crossAxisCount: 3,
                crossAxisSpacing: 10,
                mainAxisSpacing: 10,
                children: [
                  buildScoreButton("One", 1, Colors.green),
                  buildScoreButton("Two", 2, Colors.teal),
                  buildScoreButton("Three", 3, Colors.orange),
                  buildScoreButton("Four", 4, Colors.blue),
                  buildScoreButton("Six", 6, Colors.purple),
                  buildScoreButton("Wicket", 0, Colors.red, isWicket: true),
                  buildScoreButton("Wide", 1, Colors.yellow, isExtraBall: true),
                  buildScoreButton("No Ball", 1, Colors.amber, isExtraBall: true),
                  buildScoreButton("Ball Again", 0, Colors.brown, isExtraBall: true),
                ],
              ),
            ),

            // Next Innings or Finish Match
            if (isTeam1Batting)
              ElevatedButton(
                onPressed: nextInnings,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text(
                  "Next Innings",
                  style: TextStyle(fontSize: 18),
                ),
              ),
          ],
        ),
      ),
    );
  }

  // Build Button Widget for Scoring
  Widget buildScoreButton(String label, int runs, Color color,
      {bool isWicket = false, bool isExtraBall = false}) {
    return ElevatedButton(
      onPressed: () => updateScore(runs, isWicket: isWicket, isExtraBall: isExtraBall),
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        padding: const EdgeInsets.all(12),
      ),
      child: Text(
        label,
        textAlign: TextAlign.center,
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

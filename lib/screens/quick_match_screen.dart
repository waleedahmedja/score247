import 'package:flutter/material.dart';

class QuickMatchScreen extends StatefulWidget {
  final String team1Name;
  final String team2Name;

  const QuickMatchScreen({
    super.key,
    required this.team1Name,
    required this.team2Name,
  });

  @override
  _QuickMatchScreenState createState() => _QuickMatchScreenState();
}

class _QuickMatchScreenState extends State<QuickMatchScreen> {
  bool isTeam1Batting = true;
  int runsScored = 0;
  int wicketsLost = 0;
  int totalBalls = 0;

  // Store scores for both teams
  late Map<String, dynamic> team1Stats;
  late Map<String, dynamic> team2Stats;

  @override
  void initState() {
    super.initState();
    team1Stats = {"runs": 0, "wickets": 0, "balls": 0};
    team2Stats = {"runs": 0, "wickets": 0, "balls": 0};
  }

  // Update score for the current batting team
  void scoreRun(int runs) {
    setState(() {
      runsScored += runs;
      totalBalls++;

      if (isTeam1Batting) {
        team1Stats["runs"] += runs;
        team1Stats["balls"]++;
      } else {
        team2Stats["runs"] += runs;
        team2Stats["balls"]++;
      }

      checkOverEnd();
      checkInningsEnd();
    });
  }

  // Handle a wicket
  void loseWicket() {
    setState(() {
      wicketsLost++;

      if (isTeam1Batting) {
        team1Stats["wickets"]++;
      } else {
        team2Stats["wickets"]++;
      }

      totalBalls++;
      checkInningsEnd();
    });
  }

  // Check if an over has ended
  void checkOverEnd() {
    if (totalBalls % 6 == 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("End of the over!")),
      );
    }
  }

  // Check if innings should end
  void checkInningsEnd() {
    if (wicketsLost == 10 || totalBalls == 120) {
      if (isTeam1Batting) {
        // Switch innings
        isTeam1Batting = false;
        runsScored = team2Stats["runs"];
        wicketsLost = team2Stats["wickets"];
        totalBalls = team2Stats["balls"];
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Innings ended! Team 2 starts batting.")),
        );
      } else {
        // End match
        String winner = determineWinner();
        showDialog(
          context: context,
          builder: (context) {
            return AlertDialog(
              title: const Text("Match Over"),
              content: Text(winner),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text("OK"),
                ),
              ],
            );
          },
        );
      }
    }
  }

  // Determine the match winner
  String determineWinner() {
    if (team1Stats["runs"] > team2Stats["runs"]) {
      return "${widget.team1Name} wins by ${team1Stats["runs"] - team2Stats["runs"]} runs!";
    } else if (team2Stats["runs"] > team1Stats["runs"]) {
      return "${widget.team2Name} wins by ${10 - team2Stats["wickets"]} wickets!";
    } else {
      return "The match is a tie!";
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: Text("${widget.team1Name} vs ${widget.team2Name}"),
        backgroundColor: Colors.blueAccent,
      ),
      body: Column(
        children: [
          // Scorecard
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Card(
              color: Colors.grey[800],
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
              elevation: 5,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Score: $runsScored/$wicketsLost",
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      "Overs: ${totalBalls ~/ 6}.${totalBalls % 6}",
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 18,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          const SizedBox(height: 20),

          // Control buttons
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              buildScoreButton("One", 1),
              buildScoreButton("Two", 2),
              buildScoreButton("Three", 3),
              buildScoreButton("Four", 4),
              buildScoreButton("Six", 6),
              ElevatedButton(
                onPressed: loseWicket,
                style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                child: const Text("Wicket"),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // Build score button
  Widget buildScoreButton(String label, int runs) {
    return ElevatedButton(
      onPressed: () => scoreRun(runs),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.green,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
      ),
      child: Text(label),
    );
  }
}

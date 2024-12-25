import 'package:flutter/material.dart';
import '../models/player.dart';
import '../models/partnership.dart';

class MatchScreen extends StatefulWidget {
  final String team1Name;
  final String team2Name;
  final List<String> team1Players;
  final List<String> team2Players;

  const MatchScreen({
    super.key,
    required this.team1Name,
    required this.team2Name,
    required this.team1Players,
    required this.team2Players,
  });

  @override
  _MatchScreenState createState() => _MatchScreenState();
}

class _MatchScreenState extends State<MatchScreen> {
  // Match state
  late List<Player> team1;
  late List<Player> team2;

  bool isTeam1Batting = true;
  int strikerIndex = 0;
  int nonStrikerIndex = 1;
  int currentBowlerIndex = 0;

  int totalBalls = 0; // Total balls bowled in the innings
  int runsScored = 0;
  int wicketsLost = 0;

  Partnership partnership = Partnership();

  @override
  void initState() {
    super.initState();
    // Initialize teams with player names
    team1 = widget.team1Players.map((name) => Player(name: name)).toList();
    team2 = widget.team2Players.map((name) => Player(name: name)).toList();
  }

  // Update score when a run is scored
  void scoreRun(int runs) {
    setState(() {
      runsScored += runs;
      totalBalls++;

      // Update batsman's stats
      team1[strikerIndex].runs += runs;
      team1[strikerIndex].ballsFaced++;
      if (runs == 4) team1[strikerIndex].fours++;
      if (runs == 6) team1[strikerIndex].sixes++;

      // Update partnership stats
      partnership.runs += runs;
      partnership.balls++;

      // Rotate strike for odd runs
      if (runs % 2 != 0) {
        rotateStrike();
      }
      checkInningsEnd();
    });
  }

  // Handle a wicket
  void loseWicket() {
    setState(() {
      wicketsLost++;
      totalBalls++;
      partnership = Partnership(); // Reset partnership for new batsman

      // Advance to next batsman
      if (wicketsLost < team1.length - 1) {
        strikerIndex = wicketsLost + 1;
      } else {
        checkInningsEnd();
      }
    });
  }

  // Rotate strike between batsmen
  void rotateStrike() {
    setState(() {
      final temp = strikerIndex;
      strikerIndex = nonStrikerIndex;
      nonStrikerIndex = temp;
    });
  }

  // Check if innings should end
  void checkInningsEnd() {
    if (wicketsLost == team1.length - 1 || totalBalls == 120) {
      // Switch innings
      setState(() {
        isTeam1Batting = !isTeam1Batting;
        totalBalls = 0;
        runsScored = 0;
        wicketsLost = 0;
        partnership = Partnership();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentTeam = isTeam1Batting ? team1 : team2;

    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: Text(isTeam1Batting ? widget.team1Name : widget.team2Name),
        backgroundColor: Colors.blueAccent,
      ),
      body: Column(
        children: [
          // Scorecard
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Card(
              color: Colors.grey[800],
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              elevation: 5,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Score: $runsScored/$wicketsLost",
                      style: const TextStyle(color: Colors.white, fontSize: 24),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      "Overs: ${totalBalls ~/ 6}.${totalBalls % 6}",
                      style: const TextStyle(color: Colors.white70, fontSize: 18),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Partnership stats
          Card(
            color: Colors.grey[800],
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            elevation: 5,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Current Partnership",
                    style: TextStyle(color: Colors.white, fontSize: 20),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    "Runs: ${partnership.runs}, Balls: ${partnership.balls}",
                    style: const TextStyle(color: Colors.white70, fontSize: 16),
                  ),
                  Text(
                    "Run Rate: ${partnership.runRate.toStringAsFixed(2)}",
                    style: const TextStyle(color: Colors.white70, fontSize: 16),
                  ),
                ],
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
              ElevatedButton(
                onPressed: rotateStrike,
                style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
                child: const Text("Rotate Strike"),
              ),
            ],
          ),

          const SizedBox(height: 20),

          // Player stats
          Expanded(
            child: ListView.builder(
              itemCount: currentTeam.length,
              itemBuilder: (context, index) {
                final player = currentTeam[index];
                return ListTile(
                  title: Text(
                    player.name,
                    style: const TextStyle(color: Colors.white),
                  ),
                  subtitle: Text(
                    "Runs: ${player.runs}, Balls: ${player.ballsFaced}, Strike Rate: ${player.strikeRate.toStringAsFixed(2)}",
                    style: const TextStyle(color: Colors.white70),
                  ),
                  trailing: Text(
                    "Fours: ${player.fours}, Sixes: ${player.sixes}",
                    style: const TextStyle(color: Colors.white70),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  // Build control button
  Widget buildScoreButton(String label, int runs) {
    return ElevatedButton(
      onPressed: () => scoreRun(runs),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.green,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
      child: Text(label),
    );
  }
}

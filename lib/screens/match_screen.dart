import 'package:flutter/material.dart';
import '../models/player.dart';
import '../models/partnership.dart';
import 'leaderboard_screen.dart';

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
  late List<Player> battingTeam;
  late List<Player> bowlingTeam;

  bool isTeam1Batting = true;
  int strikerIndex = 0;
  int nonStrikerIndex = 1;
  int currentBowlerIndex = 0;

  int totalBalls = 0; // Total balls bowled in the innings
  int runsScored = 0;
  int wicketsLost = 0;

  List<String> matchEvents = [];
  List<String> actionHistory = [];

  Partnership partnership = Partnership();

  @override
  void initState() {
    super.initState();
    // Initialize teams
    battingTeam = widget.team1Players.map((name) => Player(name: name)).toList();
    bowlingTeam = widget.team2Players.map((name) => Player(name: name)).toList();
  }

  // Handle scoring
  void scoreRun(int runs) {
    setState(() {
      runsScored += runs;
      totalBalls++;

      // Update striker stats
      final striker = battingTeam[strikerIndex];
      striker.addRuns(runs);

      // Update bowler stats
      final bowler = bowlingTeam[currentBowlerIndex];
      bowler.addBowlingStats(runs);

      // Add match event
      addMatchEvent("Player ${striker.name} scored $runs runs.");

      // Rotate strike for odd runs
      if (runs % 2 != 0) rotateStrike();

      checkOverEnd();
      checkInningsEnd();
    });
  }

  // Handle wickets
  void loseWicket() {
    setState(() {
      wicketsLost++;
      totalBalls++;

      final bowler = bowlingTeam[currentBowlerIndex];
      bowler.addWicket();

      addMatchEvent("Wicket! Player ${battingTeam[strikerIndex].name} is out.");

      if (wicketsLost < battingTeam.length - 1) {
        strikerIndex = wicketsLost + 1; // Next batsman
      } else {
        checkInningsEnd();
      }

      checkOverEnd();
    });
  }

  // Rotate strike
  void rotateStrike() {
    setState(() {
      final temp = strikerIndex;
      strikerIndex = nonStrikerIndex;
      nonStrikerIndex = temp;
    });
  }

  // Check if over has ended
  void checkOverEnd() {
    if (totalBalls % 6 == 0) {
      addMatchEvent("End of the over.");
      selectNewBowler();
    }
  }

  // Select a new bowler
  void selectNewBowler() {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return ListView.builder(
          itemCount: bowlingTeam.length,
          itemBuilder: (context, index) {
            return ListTile(
              title: Text(
                bowlingTeam[index].name,
                style: const TextStyle(color: Colors.white),
              ),
              onTap: () {
                setState(() {
                  currentBowlerIndex = index;
                });
                Navigator.pop(context);
              },
            );
          },
        );
      },
    );
  }

  // Check if innings should end
  void checkInningsEnd() {
    if (wicketsLost == battingTeam.length - 1 || totalBalls == 120) {
      addMatchEvent("Innings ended with $runsScored/$wicketsLost.");
      // Switch innings
      setState(() {
        isTeam1Batting = !isTeam1Batting;
        battingTeam = isTeam1Batting
            ? widget.team1Players.map((name) => Player(name: name)).toList()
            : widget.team2Players.map((name) => Player(name: name)).toList();
        bowlingTeam = isTeam1Batting
            ? widget.team2Players.map((name) => Player(name: name)).toList()
            : widget.team1Players.map((name) => Player(name: name)).toList();

        // Reset stats for the new innings
        totalBalls = 0;
        runsScored = 0;
        wicketsLost = 0;
        partnership.reset();
      });
    }
  }

  // Add match event
  void addMatchEvent(String event) {
    setState(() {
      matchEvents.add(event);
    });
  }

  // Undo last action
  void undoLastAction() {
    if (actionHistory.isNotEmpty) {
      setState(() {
        final lastAction = actionHistory.removeLast();
        // Logic to undo the action (e.g., subtract runs, restore a wicket, etc.)
      });
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
          buildScorecard(),
          const SizedBox(height: 20),

          // Bowler Stats
          buildBowlerStats(),
          const SizedBox(height: 20),

          // Match Events
          Expanded(
            child: ListView.builder(
              itemCount: matchEvents.length,
              itemBuilder: (context, index) {
                return ListTile(
                  title: Text(
                    matchEvents[index],
                    style: const TextStyle(color: Colors.white),
                  ),
                );
              },
            ),
          ),

          // Control Buttons
          Wrap(
            spacing: 8,
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

  Widget buildScorecard() {
    return Card(
      color: Colors.grey[800],
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
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
    );
  }

  Widget buildBowlerStats() {
    final bowler = bowlingTeam[currentBowlerIndex];
    return Card(
      color: Colors.grey[800],
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Current Bowler",
              style: TextStyle(color: Colors.white, fontSize: 20),
            ),
            const SizedBox(height: 10),
            Text(
              "Name: ${bowler.name}",
              style: const TextStyle(color: Colors.white70, fontSize: 16),
            ),
            Text(
              "Overs: ${bowler.ballsBowled ~/ 6}.${bowler.ballsBowled % 6}",
              style: const TextStyle(color: Colors.white70, fontSize: 16),
            ),
            Text(
              "Runs Conceded: ${bowler.runsConceded}",
              style: const TextStyle(color: Colors.white70, fontSize: 16),
            ),
            Text(
              "Wickets: ${bowler.wickets}",
              style: const TextStyle(color: Colors.white70, fontSize: 16),
            ),
            Text(
              "Economy: ${bowler.economyRate.toStringAsFixed(2)}",
              style: const TextStyle(color: Colors.white70, fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }

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

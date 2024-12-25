// match_screen.dart
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
  late List<Player> battingTeam;
  late List<Player> bowlingTeam;

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
    final team1 =
        widget.team1Players.map((name) => Player(name: name)).toList();
    final team2 =
        widget.team2Players.map((name) => Player(name: name)).toList();

    battingTeam = team1;
    bowlingTeam = team2;
  }

  // Update score and bowler stats
  void scoreRun(int runs) {
    setState(() {
      runsScored += runs;
      totalBalls++;

      // Update batsman's stats
      final striker = battingTeam[strikerIndex];
      striker.runs += runs;
      striker.ballsFaced++;
      if (runs == 0) {
        striker.dotBalls++;
      } else if (runs == 4) {
        striker.fours++;
      } else if (runs == 6) {
        striker.sixes++;
      }

      // Update bowler stats
      final bowler = bowlingTeam[currentBowlerIndex];
      bowler.runsConceded += runs;
      bowler.ballsBowled++;

      // Rotate strike for odd runs
      if (runs % 2 != 0) rotateStrike();

      checkOverEnd();
      checkInningsEnd();
    });
  }

  // Handle a wicket
  void loseWicket() {
    setState(() {
      wicketsLost++;
      totalBalls++;
      partnership = Partnership(); // Reset partnership for new batsman

      // Update bowler's stats
      bowlingTeam[currentBowlerIndex].wickets++;

      // Advance to next batsman
      if (wicketsLost < battingTeam.length - 1) {
        strikerIndex = wicketsLost + 1;
      } else {
        checkInningsEnd();
      }

      checkOverEnd();
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

  // Check if an over has ended
  void checkOverEnd() {
    if (totalBalls % 6 == 0) {
      // Over ended, allow bowler selection
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
      // Switch innings
      setState(() {
        isTeam1Batting = !isTeam1Batting;
        battingTeam = isTeam1Batting
            ? widget.team1Players.map((name) => Player(name: name)).toList()
            : widget.team2Players.map((name) => Player(name: name)).toList();
        bowlingTeam = isTeam1Batting
            ? widget.team2Players.map((name) => Player(name: name)).toList()
            : widget.team1Players.map((name) => Player(name: name)).toList();
        totalBalls = 0;
        runsScored = 0;
        wicketsLost = 0;
        partnership = Partnership();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
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
                      style: const TextStyle(color: Colors.white, fontSize: 24),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      "Overs: ${totalBalls ~/ 6}.${totalBalls % 6}",
                      style:
                          const TextStyle(color: Colors.white70, fontSize: 18),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Current Bowler Stats
          Card(
            color: Colors.grey[800],
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            elevation: 5,
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
                    "Name: ${bowlingTeam[currentBowlerIndex].name}",
                    style: const TextStyle(color: Colors.white70, fontSize: 16),
                  ),
                  Text(
                    "Overs: ${bowlingTeam[currentBowlerIndex].ballsBowled ~/ 6}.${bowlingTeam[currentBowlerIndex].ballsBowled % 6}",
                    style: const TextStyle(color: Colors.white70, fontSize: 16),
                  ),
                  Text(
                    "Runs Conceded: ${bowlingTeam[currentBowlerIndex].runsConceded}",
                    style: const TextStyle(color: Colors.white70, fontSize: 16),
                  ),
                  Text(
                    "Wickets: ${bowlingTeam[currentBowlerIndex].wickets}",
                    style: const TextStyle(color: Colors.white70, fontSize: 16),
                  ),
                  Text(
                    "Economy: ${bowlingTeam[currentBowlerIndex].economyRate.toStringAsFixed(2)}",
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
            ],
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
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Runs: ${player.runs}, Balls: ${player.ballsFaced}, Strike Rate: ${player.strikeRate.toStringAsFixed(2)}",
              style: const TextStyle(color: Colors.white70),
            ),
            Text(
              "Fours: ${player.fours}, Sixes: ${player.sixes}, Dot Balls: ${player.dotBalls}",
              style: const TextStyle(color: Colors.white70),
            ),
          ],
        ),
      );
    },
  ),
),
class MatchScreen extends StatefulWidget {
  final String team1Name;
  final String team2Name;
  final int oversPerMatch;

  const MatchScreen({
    super.key,
    required this.team1Name,
    required this.team2Name,
    required this.oversPerMatch,
  });

  @override
  _MatchScreenState createState() => _MatchScreenState();
}

class _MatchScreenState extends State<MatchScreen> {
  void endMatch() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => LeaderboardScreen(players: []), // Pass player stats here
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: Text(widget.team1Name + " vs " + widget.team2Name),
        backgroundColor: Colors.blueAccent,
      ),
      body: Center(
        child: ElevatedButton(
          onPressed: endMatch,
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red,
            padding: const EdgeInsets.symmetric(vertical: 16),
          ),
          child: const Text(
            "End Match and View Leaderboard",
            style: TextStyle(fontSize: 18),
          ),
        ),
      ),
    );
  }
}
Expanded(
  child: ListView.builder(
    itemCount: battingTeam.length,
    itemBuilder: (context, index) {
      final player = battingTeam[index];
      return ListTile(
        title: Text(
          player.name,
          style: const TextStyle(color: Colors.white),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Runs: ${player.runs}, Balls: ${player.ballsFaced}, Strike Rate: ${player.strikeRate.toStringAsFixed(2)}",
              style: const TextStyle(color: Colors.white70),
            ),
            Text(
              "Fours: ${player.fours}, Sixes: ${player.sixes}, Dot Balls: ${player.dotBalls}",
              style: const TextStyle(color: Colors.white70),
            ),
          ],
        ),
      );
    },
  ),
),
List<String> matchEvents = [];

void addMatchEvent(String event) {
  setState(() {
    matchEvents.add(event);
  });
}
void scoreRun(int runs) {
  setState(() {
    runsScored += runs;
    addMatchEvent("Player ${striker.name} scored $runs runs.");
  });
}
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
List<String> actionHistory = [];

void undoLastAction() {
  if (actionHistory.isNotEmpty) {
    final lastAction = actionHistory.removeLast();
    // Revert the last action (e.g., subtract runs, restore wicket, etc.)
    setState(() {
      // Undo logic here
    });
  }
}
ElevatedButton(
  onPressed: undoLastAction,
  child: const Text("Undo Last Action"),
),

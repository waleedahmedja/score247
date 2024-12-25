import 'package:flutter/material.dart';
import '../models/dls_calculator.dart';

class DLSScreen extends StatefulWidget {
  final int team1Score;

  const DLSScreen({super.key, required this.team1Score});

  @override
  _DLSScreenState createState() => _DLSScreenState();
}

class _DLSScreenState extends State<DLSScreen> {
  int oversRemaining = 20;
  double resourcesAvailable = 46.7; // Default resources for 20 overs

  @override
  Widget build(BuildContext context) {
    final adjustedTarget = DLSCalculator.calculateTarget(
      widget.team1Score,
      oversRemaining,
      resourcesAvailable,
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text("DLS Calculator"),
        backgroundColor: Colors.blueAccent,
      ),
      backgroundColor: Colors.grey[900],
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Duckworth-Lewis Method",
              style: TextStyle(color: Colors.white, fontSize: 24),
            ),
            const SizedBox(height: 20),

            // Input for overs remaining
            const Text(
              "Overs Remaining:",
              style: TextStyle(color: Colors.white, fontSize: 16),
            ),
            Slider(
              value: oversRemaining.toDouble(),
              min: 0,
              max: 50,
              divisions: 50,
              label: "$oversRemaining overs",
              onChanged: (value) {
                setState(() {
                  oversRemaining = value.toInt();
                  resourcesAvailable = DLSCalculator.resourcesTable[oversRemaining] ?? 0.0;
                });
              },
            ),

            const SizedBox(height: 20),

            // Display adjusted target
            Card(
              color: Colors.grey[800],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  "Adjusted Target: $adjustedTarget",
                  style: const TextStyle(color: Colors.white, fontSize: 20),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

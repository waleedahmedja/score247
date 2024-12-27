import 'package:flutter/material.dart';
import '../models/dls_calculator.dart';

class DLSScreen extends StatefulWidget {
  final int team1Score;

  const DLSScreen({super.key, required this.team1Score});

  @override
  _DLSScreenState createState() => _DLSScreenState();
}

class _DLSScreenState extends State<DLSScreen> {
  int oversRemaining = 20; // Default value for overs remaining
  double resourcesAvailable = 46.7; // Default resources for 20 overs
  late int adjustedTarget; // Adjusted target score

  @override
  void initState() {
    super.initState();
    _calculateAdjustedTarget(); // Calculate initial target
  }

  // Function to calculate the adjusted target
  void _calculateAdjustedTarget() {
    try {
      // Ensure valid inputs for team1Score and oversRemaining
      if (widget.team1Score < 0 || oversRemaining < 0 || oversRemaining > 50) {
        throw ArgumentError("Invalid inputs for DLS calculation");
      }

      resourcesAvailable = DLSCalculator.getResourcePercentage(oversRemaining);
      adjustedTarget = DLSCalculator.calculateTarget(
        widget.team1Score,
        oversRemaining,
      );
    } catch (e) {
      adjustedTarget = 0; // Fallback value for invalid input
    }
  }

  @override
  Widget build(BuildContext context) {
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
            // Title
            const Text(
              "Duckworth-Lewis Method",
              style: TextStyle(color: Colors.white, fontSize: 24),
            ),
            const SizedBox(height: 20),

            // Overs Remaining Input
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
                  _calculateAdjustedTarget(); // Recalculate target dynamically
                });
              },
            ),

            const SizedBox(height: 20),

            // Display Adjusted Target
            Card(
              color: Colors.grey[800],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "Adjusted Target:",
                      style: TextStyle(color: Colors.white70, fontSize: 18),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      "$adjustedTarget",
                      style: const TextStyle(color: Colors.white, fontSize: 20),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Additional Information
            Text(
              "Resources Available: ${resourcesAvailable.toStringAsFixed(2)}%",
              style: const TextStyle(color: Colors.white70, fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}

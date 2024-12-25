// dls_calculator.dart
class DLSCalculator {
  // Basic resource percentage table
  static const Map<int, double> resourcesTable = {
    50: 100.0,
    45: 92.2,
    40: 83.6,
    35: 74.9,
    30: 65.8,
    25: 56.4,
    20: 46.7,
    15: 36.7,
    10: 26.3,
    5: 13.4,
    0: 0.0,
  };

  // Calculate target score
  static int calculateTarget(
    int team1Score,
    int oversRemaining,
    double resourceRemaining,
  ) {
    final double team1Resources = resourcesTable[50]!; // Assume Team 1 batted full 50 overs
    final double team2Resources = resourceRemaining;

    // Calculate resource percentage
    double resourcePercentage = team2Resources / team1Resources;

    // Adjusted target score
    return (team1Score * resourcePercentage).ceil();
  }
}

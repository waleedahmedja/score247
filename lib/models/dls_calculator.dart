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

  // Linear interpolation for resource percentage
  static double getResourcePercentage(int oversRemaining) {
    if (resourcesTable.containsKey(oversRemaining)) {
      return resourcesTable[oversRemaining]!;
    }

    // Find closest lower and upper bounds for oversRemaining
    final lowerKey = resourcesTable.keys.where((k) => k < oversRemaining).reduce((a, b) => a > b ? a : b);
    final upperKey = resourcesTable.keys.where((k) => k > oversRemaining).reduce((a, b) => a < b ? a : b);

    // Interpolate between lower and upper bounds
    final lowerValue = resourcesTable[lowerKey]!;
    final upperValue = resourcesTable[upperKey]!;
    final fraction = (oversRemaining - lowerKey) / (upperKey - lowerKey);

    return lowerValue + (upperValue - lowerValue) * fraction;
  }

  // Calculate target score
  static int calculateTarget(
    int team1Score,
    int oversRemaining,
  ) {
    // Validate inputs
    if (oversRemaining < 0 || oversRemaining > 50) {
      throw ArgumentError("Overs remaining must be between 0 and 50");
    }

    // Team 1 resources are always based on 50 overs (max resources)
    final double team1Resources = resourcesTable[50]!;

    // Get Team 2's remaining resources
    final double team2Resources = getResourcePercentage(oversRemaining);

    // Calculate resource percentage
    final double resourcePercentage = team2Resources / team1Resources;

    // Adjusted target score
    return (team1Score * resourcePercentage).ceil();
  }
}

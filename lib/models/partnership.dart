class Partnership {
  int runs = 0; // Total runs scored in the partnership
  int balls = 0; // Total balls faced in the partnership

  Partnership();

  /// Calculate the run rate for the partnership.
  /// Run rate is calculated as runs scored per over (6 balls).
  double get runRate => balls == 0 ? 0 : (runs / balls) * 6;

  /// Increment runs and balls for the partnership.
  void addRuns(int additionalRuns) {
    runs += additionalRuns;
    balls++;
  }

  /// Reset the partnership stats.
  void reset() {
    runs = 0;
    balls = 0;
  }
}

// partnership.dart
class Partnership {
  int runs = 0;
  int balls = 0;

  Partnership();

  // Calculate run rate
  double get runRate => balls == 0 ? 0 : (runs / balls) * 6;
}

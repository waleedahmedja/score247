import 'package:flutter/material.dart';
import 'screens/setup_screen.dart';

void main() {
  runApp(const Score247App());
}

class Score247App extends StatelessWidget {
  const Score247App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Score247',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const SetupScreen(),
    );
  }
}
import 'package:flutter/material.dart';
import 'screens/setup_screen.dart';
import 'screens/toss_screen.dart';
import 'screens/match_screen.dart';

void main() {
  runApp(const Score247App());
}

class Score247App extends StatelessWidget {
  const Score247App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Score247',
      initialRoute: '/',
      routes: {
        '/': (context) => const SetupScreen(),
        '/toss': (context) => const TossScreen(),
        '/match': (context) => const MatchScreen(),
      },
    );
  }
}

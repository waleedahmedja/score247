import 'package:flutter/material.dart';
import 'toss_screen.dart';
import '../widgets/dropdown_widget.dart';
import '../widgets/toggle_widget.dart';

class SetupScreen extends StatefulWidget {
  const SetupScreen({super.key});

  @override
  _SetupScreenState createState() => _SetupScreenState();
}

class _SetupScreenState extends State<SetupScreen> {
  int? selectedPlayers; // Players per team
  String? selectedOvers; // Number of overs
  String selectedToss = "Heads"; // Default toss option

  final List<int> playerOptions = [4, 5, 6, 7, 8, 9];
  final List<String> overOptions = ['1', '2', '3', '4', '5', '6', 'Unlimited'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        title: const Text('Match Setup'),
        backgroundColor: Colors.blueAccent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Dropdown for selecting players
            DropdownWidget<int>(
              title: 'Select Players Per Team:',
              value: selectedPlayers,
              options: playerOptions,
              onChanged: (value) {
                setState(() {
                  selectedPlayers = value;
                });
              },
            ),
            const SizedBox(height: 20),

            // Dropdown for selecting overs
            DropdownWidget<String>(
              title: 'Select Number of Overs:',
              value: selectedOvers,
              options: overOptions,
              onChanged: (value) {
                setState(() {
                  selectedOvers = value;
                });
              },
            ),
            const SizedBox(height: 20),

            // Toggle for selecting Heads or Tails
            ToggleWidget(
              title: 'Select Toss:',
              options: ['Heads', 'Tails'],
              selectedValue: selectedToss,
              onSelected: (value) {
                setState(() {
                  selectedToss = value;
                });
              },
            ),
            const SizedBox(height: 30),

            // Proceed button
            ElevatedButton(
              onPressed: () {
                if (selectedPlayers != null && selectedOvers != null) {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => TossScreen(
                        selectedPlayers: selectedPlayers!,
                        selectedOvers: selectedOvers!,
                        selectedToss: selectedToss,
                      ),
                    ),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Please fill all the fields'),
                    ),
                  );
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text(
                'Proceed to Toss',
                style: TextStyle(fontSize: 18),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

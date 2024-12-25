// toggle_widget.dart
import 'package:flutter/material.dart';

class ToggleWidget extends StatelessWidget {
  final String title;
  final List<String> options;
  final String selectedValue;
  final ValueChanged<String> onSelected;

  const ToggleWidget({
    super.key,
    required this.title,
    required this.options,
    required this.selectedValue,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(color: Colors.white, fontSize: 16),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: options.map((option) {
            return ChoiceChip(
              label: Text(option),
              selected: selectedValue == option,
              onSelected: (selected) {
                if (selected) onSelected(option);
              },
              selectedColor: Colors.blue,
              backgroundColor: Colors.grey[800],
              labelStyle: TextStyle(
                color: selectedValue == option
                    ? Colors.white
                    : Colors.grey[400],
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}

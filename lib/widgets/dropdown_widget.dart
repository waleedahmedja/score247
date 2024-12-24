import 'package:flutter/material.dart';

class DropdownWidget<T> extends StatelessWidget {
  final String title;
  final T? value;
  final List<T> options;
  final ValueChanged<T?> onChanged;

  const DropdownWidget({
    super.key,
    required this.title,
    required this.value,
    required this.options,
    required this.onChanged,
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
        DropdownButtonFormField<T>(
          value: value,
          onChanged: onChanged,
          items: options
              .map((option) =>
                  DropdownMenuItem(value: option, child: Text(option.toString())))
              .toList(),
          decoration: InputDecoration(
            filled: true,
            fillColor: Colors.grey[800],
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
          dropdownColor: Colors.grey[800],
          style: const TextStyle(color: Colors.white),
        ),
      ],
    );
  }
}

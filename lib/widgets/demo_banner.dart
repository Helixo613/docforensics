// lib/widgets/demo_banner.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class DemoBanner extends StatelessWidget {
  const DemoBanner({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      color: const Color(0xFF1A1714),
      child: Row(
        children: [
          const Icon(Icons.info_outline_rounded,
              color: Color(0xFFFACC15), size: 15),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'Demo mode — backend unavailable. Showing sample data.',
              style: GoogleFonts.inter(
                fontSize: 12,
                color: const Color(0xFFFACC15),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

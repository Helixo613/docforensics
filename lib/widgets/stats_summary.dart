// lib/widgets/stats_summary.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/constants.dart';
import '../models/analysis_result.dart';

class StatsSummary extends StatelessWidget {
  final ResultStats stats;

  const StatsSummary({super.key, required this.stats});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(AppColors.borderValue)),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          _StatItem(
            value: stats.contradictionsFound.toString(),
            label: 'Contradictions',
            color: const Color(AppColors.contradictionColorValue),
          ),
          _divider(),
          _StatItem(
            value: stats.agreementsFound.toString(),
            label: 'Agreements',
            color: const Color(AppColors.agreementColorValue),
          ),
          _divider(),
          _StatItem(
            value: stats.uncorroboratedCount.toString(),
            label: 'Solo claims',
            color: const Color(AppColors.uncorroboratedColorValue),
          ),
          _divider(),
          _StatItem(
            value: stats.totalSentences.toString(),
            label: 'Sentences',
            color: const Color(AppColors.textSecondaryValue),
          ),
        ],
      ),
    );
  }

  Widget _divider() => Container(
        height: 32,
        width: 1,
        margin: const EdgeInsets.symmetric(horizontal: 12),
        color: const Color(AppColors.borderValue),
      );
}

class _StatItem extends StatelessWidget {
  final String value;
  final String label;
  final Color color;

  const _StatItem({
    required this.value,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Text(
            value,
            style: GoogleFonts.inter(
              fontSize: 22,
              fontWeight: FontWeight.w700,
              color: color,
              height: 1,
            ),
          ),
          const SizedBox(height: 3),
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 10,
              color: const Color(AppColors.textTertiaryValue),
              letterSpacing: 0.2,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

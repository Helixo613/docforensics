// lib/screens/results_screen.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/constants.dart';
import '../models/analysis_result.dart';
import '../widgets/demo_banner.dart';
import '../widgets/finding_card.dart';
import '../widgets/stats_summary.dart';

class ResultsScreen extends StatefulWidget {
  final AnalysisResult result;

  const ResultsScreen({super.key, required this.result});

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  AnalysisResult get r => widget.result;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(AppColors.surfaceValue),
      body: SafeArea(
        child: Column(
          children: [
            if (r.isDemoData) const DemoBanner(),
            _buildHeader(),
            _buildTabs(),
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildContradictionsTab(),
                  _buildAgreementsTab(),
                  _buildUncorroboratedTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              IconButton(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.arrow_back_ios_new_rounded,
                    size: 18,
                    color: Color(AppColors.textSecondaryValue)),
                padding: EdgeInsets.zero,
                constraints:
                    const BoxConstraints(minWidth: 32, minHeight: 32),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Consensus Brief',
                  style: GoogleFonts.playfairDisplay(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: const Color(AppColors.textPrimaryValue),
                  ),
                ),
              ),
            ],
          ),

          // Gemini summary
          if (r.geminiSummary != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color:
                    const Color(AppColors.accentValue).withOpacity(0.05),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                    color: const Color(AppColors.accentValue)
                        .withOpacity(0.15)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.auto_awesome,
                      size: 14,
                      color: Color(AppColors.accentValue)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      r.geminiSummary!,
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        height: 1.55,
                        color: const Color(AppColors.textSecondaryValue),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],

          const SizedBox(height: 14),
          StatsSummary(stats: r.stats),
        ],
      ),
    );
  }

  Widget _buildTabs() {
    return Container(
      color: Colors.white,
      child: TabBar(
        controller: _tabController,
        labelStyle: GoogleFonts.inter(
            fontSize: 13, fontWeight: FontWeight.w600),
        unselectedLabelStyle:
            GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w400),
        labelColor: const Color(AppColors.textPrimaryValue),
        unselectedLabelColor: const Color(AppColors.textTertiaryValue),
        indicatorSize: TabBarIndicatorSize.tab,
        indicatorColor: const Color(AppColors.accentValue),
        indicatorWeight: 2,
        dividerColor: const Color(AppColors.borderValue),
        tabs: [
          Tab(
            child: _TabLabel(
              label: 'Contradictions',
              count: r.contradictions.length,
              color: const Color(AppColors.contradictionColorValue),
            ),
          ),
          Tab(
            child: _TabLabel(
              label: 'Agreements',
              count: r.agreements.length,
              color: const Color(AppColors.agreementColorValue),
            ),
          ),
          Tab(
            child: _TabLabel(
              label: 'Solo',
              count: r.uncorroborated.length,
              color: const Color(AppColors.uncorroboratedColorValue),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContradictionsTab() {
    if (r.contradictions.isEmpty) {
      return _EmptyState(
        icon: Icons.check_circle_outline_rounded,
        message: 'No contradictions found',
        sub: 'The uploaded documents appear to be consistent.',
        color: const Color(AppColors.agreementColorValue),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: r.contradictions.length,
      itemBuilder: (_, i) => PairFindingCard(
        result: r.contradictions[i],
        type: FindingType.contradiction,
        geminiInsight: r.geminiContradictionInsights != null &&
                i < r.geminiContradictionInsights!.length
            ? r.geminiContradictionInsights![i]
            : null,
        index: i,
      ),
    );
  }

  Widget _buildAgreementsTab() {
    if (r.agreements.isEmpty) {
      return _EmptyState(
        icon: Icons.compare_arrows_rounded,
        message: 'No agreements found',
        sub: 'The documents did not produce strongly matching claims.',
        color: const Color(AppColors.textTertiaryValue),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: r.agreements.length,
      itemBuilder: (_, i) => PairFindingCard(
        result: r.agreements[i],
        type: FindingType.agreement,
        geminiInsight: r.geminiAgreementInsights != null &&
                i < r.geminiAgreementInsights!.length
            ? r.geminiAgreementInsights![i]
            : null,
        index: i,
      ),
    );
  }

  Widget _buildUncorroboratedTab() {
    if (r.uncorroborated.isEmpty) {
      return _EmptyState(
        icon: Icons.done_all_rounded,
        message: 'All claims corroborated',
        sub: 'Every claim was matched across at least two documents.',
        color: const Color(AppColors.agreementColorValue),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
          child: Text(
            'These claims appear in only one document and were not matched elsewhere.',
            style: GoogleFonts.inter(
              fontSize: 12,
              height: 1.5,
              color: const Color(AppColors.textTertiaryValue),
            ),
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
            itemCount: r.uncorroborated.length,
            itemBuilder: (_, i) => UncorroboratedCard(
              result: r.uncorroborated[i],
              index: i,
            ),
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────

class _TabLabel extends StatelessWidget {
  final String label;
  final int count;
  final Color color;

  const _TabLabel({
    required this.label,
    required this.count,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(label),
        if (count > 0) ...[
          const SizedBox(width: 5),
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
            decoration: BoxDecoration(
              color: color.withOpacity(0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              '$count',
              style: GoogleFonts.inter(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: color,
              ),
            ),
          ),
        ],
      ],
    );
  }
}

class _EmptyState extends StatelessWidget {
  final IconData icon;
  final String message;
  final String sub;
  final Color color;

  const _EmptyState({
    required this.icon,
    required this.message,
    required this.sub,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 48, color: color.withOpacity(0.4)),
            const SizedBox(height: 16),
            Text(
              message,
              style: GoogleFonts.inter(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: const Color(AppColors.textPrimaryValue),
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              sub,
              style: GoogleFonts.inter(
                fontSize: 13,
                height: 1.5,
                color: const Color(AppColors.textTertiaryValue),
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

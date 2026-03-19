// lib/screens/results_screen.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/constants.dart';
import '../models/analysis_result.dart';
import '../models/v2_models.dart';
import '../models/session_results.dart';
import '../widgets/demo_banner.dart';
import '../widgets/finding_card.dart';
import '../widgets/stats_summary.dart';
import '../widgets/v2_issue_card.dart';

class ResultsScreen extends StatefulWidget {
  final SessionResults results;

  const ResultsScreen({super.key, required this.results});

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen>
    with TickerProviderStateMixin {
  late final TabController _v1TabController;
  int _viewIndex = 0; // 0 for V1 (Evidence), 1 for V2 (Issues)

  @override
  void initState() {
    super.initState();
    _v1TabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _v1TabController.dispose();
    super.dispose();
  }

  AnalysisResult get r => widget.results.v1;
  IssueMapResponse? get v2 => widget.results.v2;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(AppColors.surfaceValue),
      body: SafeArea(
        child: Column(
          children: [
            if (r.isDemoData) const DemoBanner(),
            _buildHeader(),
            _buildViewToggle(),
            Expanded(
              child: _viewIndex == 0 ? _buildV1View() : _buildV2View(),
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
                  _viewIndex == 0 ? 'Evidence View' : 'Issue Map',
                  style: GoogleFonts.playfairDisplay(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: const Color(AppColors.textPrimaryValue),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            _viewIndex == 0
                ? 'V1 is the source-of-truth evidence layer for this session.'
                : 'V2 organizes the same evidence into issue-level structure when available.',
            style: GoogleFonts.inter(
              fontSize: 12,
              height: 1.45,
              color: const Color(AppColors.textTertiaryValue),
            ),
          ),

          // Gemini summary
          if (_viewIndex == 0 && r.geminiSummary != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color:
                    const Color(AppColors.accentValue).withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                    color: const Color(AppColors.accentValue)
                        .withValues(alpha: 0.15)),
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

          if (_viewIndex == 0) ...[
            const SizedBox(height: 14),
            StatsSummary(stats: r.stats),
          ] else if (v2 != null) ...[
            const SizedBox(height: 14),
            _buildV2StatsHeader(),
          ],
        ],
      ),
    );
  }

  Widget _buildViewToggle() {
    if (v2 == null) return const SizedBox.shrink();

    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Container(
        height: 36,
        decoration: BoxDecoration(
          color: const Color(AppColors.surfaceValue),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Expanded(
              child: _ToggleItem(
                label: 'Evidence (V1)',
                isSelected: _viewIndex == 0,
                onTap: () => setState(() => _viewIndex = 0),
              ),
            ),
            Expanded(
              child: _ToggleItem(
                label: 'Issues (V2)',
                isSelected: _viewIndex == 1,
                onTap: () => setState(() => _viewIndex = 1),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildV1View() {
    return Column(
      children: [
        _buildTabs(),
        Expanded(
          child: TabBarView(
            controller: _v1TabController,
            children: [
              _buildContradictionsTab(),
              _buildAgreementsTab(),
              _buildUncorroboratedTab(),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildV2View() {
    if (v2 == null) return const SizedBox.shrink();

    if (v2!.issues.isEmpty) {
      return const _EmptyState(
        icon: Icons.account_tree_outlined,
        message: 'No issue structure available',
        sub: 'This session is better reviewed in the Evidence View.',
        color: Color(AppColors.textTertiaryValue),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (v2!.fallback.shouldFallback) _buildV2FallbackBanner(),
        _buildV2OverviewCard(),
        const SizedBox(height: 12),
        ...v2!.issues.map((issue) => V2IssueCard(issue: issue)),
      ],
    );
  }

  Widget _buildV2StatsHeader() {
    final s = v2!.stats;
    final c = v2!.coverage;
    return Row(
      children: [
        _StatChip(
          label: 'Total Issues',
          value: '${s.totalIssues}',
          color: const Color(AppColors.accentValue),
        ),
        const SizedBox(width: 8),
        _StatChip(
          label: 'Claim Coverage',
          value: '${(c.claimCoverage * 100).toStringAsFixed(0)}%',
          color: const Color(AppColors.textSecondaryValue),
        ),
        const Spacer(),
        if (v2!.fallback.shouldFallback)
          const Icon(Icons.warning_amber_rounded,
              size: 16, color: Color(AppColors.uncorroboratedColorValue)),
      ],
    );
  }

  Widget _buildV2OverviewCard() {
    final stats = v2!.stats;
    final coverage = v2!.coverage;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(AppColors.borderValue)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Issue map coverage',
            style: GoogleFonts.inter(
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: const Color(AppColors.textPrimaryValue),
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'This is a structured lens over pair-derived evidence. Uncorroborated claims remain outside the issue map.',
            style: GoogleFonts.inter(
              fontSize: 12,
              height: 1.45,
              color: const Color(AppColors.textSecondaryValue),
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _StatChip(
                label: 'Contested',
                value: '${stats.contestedIssues}',
                color: const Color(AppColors.contradictionColorValue),
              ),
              _StatChip(
                label: 'Aligned',
                value: '${stats.alignedIssues}',
                color: const Color(AppColors.agreementColorValue),
              ),
              _StatChip(
                label: 'Mixed',
                value: '${stats.mixedIssues}',
                color: const Color(AppColors.uncorroboratedColorValue),
              ),
              _StatChip(
                label: 'Outside Map',
                value: '${coverage.uncorroboratedClaimsOutsideIssueMap}',
                color: const Color(AppColors.textSecondaryValue),
              ),
              if (coverage.structurallyAmbiguousClaimsInIssues > 0)
                _StatChip(
                  label: 'Ambiguous',
                  value: '${coverage.structurallyAmbiguousClaimsInIssues}',
                  color: const Color(AppColors.uncorroboratedColorValue),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildV2FallbackBanner() {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(AppColors.uncorroboratedBgValue),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
            color: const Color(AppColors.uncorroboratedBorderValue)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.info_outline_rounded,
              size: 16, color: Color(AppColors.uncorroboratedColorValue)),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Structure Warning',
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: const Color(AppColors.uncorroboratedColorValue),
                  ),
                ),
                const SizedBox(height: 2),
                ...v2!.fallback.reasons.map((reason) => Padding(
                  padding: const EdgeInsets.only(top: 2),
                  child: Text(
                    '• $reason',
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      height: 1.4,
                      color: const Color(AppColors.textSecondaryValue),
                    ),
                  ),
                )),
                const SizedBox(height: 4),
                Text(
                  'We recommend relying on the Evidence View for this session.',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: const Color(AppColors.textSecondaryValue),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabs() {
    return Container(
      color: Colors.white,
      child: TabBar(
        controller: _v1TabController,
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
              color: color.withValues(alpha: 0.12),
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
            Icon(icon, size: 48, color: color.withValues(alpha: 0.4)),
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

class _ToggleItem extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _ToggleItem({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.all(2),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(6),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 2,
                    offset: const Offset(0, 1),
                  )
                ]
              : null,
        ),
        alignment: Alignment.center,
        child: Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 12,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
            color: isSelected
                ? const Color(AppColors.accentValue)
                : const Color(AppColors.textSecondaryValue),
          ),
        ),
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _StatChip({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        children: [
          Text(
            '$label: ',
            style: GoogleFonts.inter(
              fontSize: 11,
              color: color.withValues(alpha: 0.7),
            ),
          ),
          Text(
            value,
            style: GoogleFonts.inter(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

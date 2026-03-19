// lib/widgets/v2_issue_card.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/constants.dart';
import '../models/v2_models.dart';

class V2IssueCard extends StatefulWidget {
  final Issue issue;

  const V2IssueCard({super.key, required this.issue});

  @override
  State<V2IssueCard> createState() => _V2IssueCardState();
}

class _V2IssueCardState extends State<V2IssueCard> {
  bool _expanded = false;

  Color get _statusColor {
    switch (widget.issue.status) {
      case 'contested':
        return const Color(AppColors.contradictionColorValue);
      case 'aligned':
        return const Color(AppColors.agreementColorValue);
      case 'mixed':
      case 'unclear':
      default:
        return const Color(AppColors.uncorroboratedColorValue);
    }
  }

  Color get _bgColor {
    switch (widget.issue.status) {
      case 'contested':
        return const Color(AppColors.contradictionBgValue);
      case 'aligned':
        return const Color(AppColors.agreementBgValue);
      case 'mixed':
      case 'unclear':
      default:
        return const Color(AppColors.uncorroboratedBgValue);
    }
  }

  Color get _borderColor {
    switch (widget.issue.status) {
      case 'contested':
        return const Color(AppColors.contradictionBorderValue);
      case 'aligned':
        return const Color(AppColors.agreementBorderValue);
      case 'mixed':
      case 'unclear':
      default:
        return const Color(AppColors.uncorroboratedBorderValue);
    }
  }

  @override
  Widget build(BuildContext context) {
    final issue = widget.issue;
    final labelMeta = issue.labelKind == 'representative_claim_excerpt'
        ? 'representative excerpt'
        : issue.labelKind;
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: _expanded ? _bgColor : Colors.white,
        border: Border.all(color: _borderColor, width: 1.5),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: _statusColor.withValues(alpha: 0.06),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            InkWell(
              onTap: () => setState(() => _expanded = !_expanded),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              _IssueChip(
                                label: issue.status,
                                color: _statusColor,
                              ),
                              const SizedBox(width: 8),
                              _QualityChip(quality: issue.structuralQuality),
                              if (issue.mergeRisk) ...[
                                const SizedBox(width: 8),
                                const _MergeRiskChip(),
                              ],
                            ],
                          ),
                          const SizedBox(height: 10),
                          Text(
                            issue.label,
                            style: GoogleFonts.inter(
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                              color: const Color(AppColors.textPrimaryValue),
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            labelMeta.isEmpty
                                ? '${issue.documentsInvolved.length} documents involved'
                                : '${issue.documentsInvolved.length} documents involved · $labelMeta',
                            style: GoogleFonts.inter(
                              fontSize: 11,
                              color: const Color(AppColors.textTertiaryValue),
                            ),
                          ),
                          if (issue.documentsInvolved.isNotEmpty) ...[
                            const SizedBox(height: 10),
                            Wrap(
                              spacing: 6,
                              runSpacing: 6,
                              children: issue.documentsInvolved
                                  .map((doc) => _DocumentChip(label: doc))
                                  .toList(),
                            ),
                          ],
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Icon(
                      _expanded
                          ? Icons.keyboard_arrow_up_rounded
                          : Icons.keyboard_arrow_down_rounded,
                      color: const Color(AppColors.textTertiaryValue),
                    ),
                  ],
                ),
              ),
            ),
            if (_expanded) ...[
              Divider(height: 1, color: _borderColor),
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (issue.sides.isNotEmpty) ...[
                      ...issue.sides.map((side) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 16),
                          child: _SideBlock(
                            sideName: _displaySideName(side.sideId),
                            claims: side.claims,
                            documents: side.documents,
                            accentColor: _statusColor,
                          ),
                        );
                      }),
                    ],
                    if (issue.mixedClaims.isNotEmpty) ...[
                      _SideBlock(
                        sideName: 'Mixed / Ambiguous',
                        claims: issue.mixedClaims,
                        documents: const [],
                        accentColor: const Color(AppColors.textTertiaryValue),
                      ),
                      const SizedBox(height: 16),
                    ],
                    if (issue.unclearClaims.isNotEmpty) ...[
                      _SideBlock(
                        sideName: 'Unclear',
                        claims: issue.unclearClaims,
                        documents: const [],
                        accentColor: const Color(AppColors.textTertiaryValue),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _displaySideName(String sideId) {
    switch (sideId) {
      case 'side_0':
        return 'Side A';
      case 'side_1':
        return 'Side B';
      default:
        return sideId.replaceAll('_', ' ');
    }
  }
}

class _IssueChip extends StatelessWidget {
  final String label;
  final Color color;

  const _IssueChip({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        label.toUpperCase(),
        style: GoogleFonts.inter(
          fontSize: 10,
          fontWeight: FontWeight.w800,
          letterSpacing: 0.5,
          color: color,
        ),
      ),
    );
  }
}

class _QualityChip extends StatelessWidget {
  final String quality;

  const _QualityChip({required this.quality});

  @override
  Widget build(BuildContext context) {
    Color color;
    switch (quality) {
      case 'clean':
        color = const Color(AppColors.agreementColorValue);
        break;
      case 'borderline':
        color = const Color(AppColors.uncorroboratedColorValue);
        break;
      default:
        color = const Color(AppColors.textTertiaryValue);
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        border: Border.all(color: color.withValues(alpha: 0.3)),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        quality,
        style: GoogleFonts.inter(
          fontSize: 9,
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
    );
  }
}

class _MergeRiskChip extends StatelessWidget {
  const _MergeRiskChip();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: const Color(AppColors.contradictionColorValue).withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.merge_type,
              size: 10, color: Color(AppColors.contradictionColorValue)),
          const SizedBox(width: 2),
          Text(
            'MERGE RISK',
            style: GoogleFonts.inter(
              fontSize: 9,
              fontWeight: FontWeight.w700,
              color: const Color(AppColors.contradictionColorValue),
            ),
          ),
        ],
      ),
    );
  }
}

class _SideBlock extends StatelessWidget {
  final String sideName;
  final List<V2Claim> claims;
  final List<String> documents;
  final Color accentColor;

  const _SideBlock({
    required this.sideName,
    required this.claims,
    required this.documents,
    required this.accentColor,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          sideName.toUpperCase(),
          style: GoogleFonts.inter(
            fontSize: 10,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.8,
            color: accentColor,
          ),
        ),
        if (documents.isNotEmpty) ...[
          const SizedBox(height: 6),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: documents
                .map((doc) => _DocumentChip(label: doc))
                .toList(),
          ),
        ],
        const SizedBox(height: 8),
        ...claims.map((claim) => _ClaimItem(claim: claim)),
      ],
    );
  }
}

class _ClaimItem extends StatelessWidget {
  final V2Claim claim;

  const _ClaimItem({required this.claim});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: const Color(AppColors.borderValue).withValues(alpha: 0.5),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '"${claim.text}"',
            style: GoogleFonts.inter(
              fontSize: 12,
              height: 1.5,
              color: const Color(AppColors.textPrimaryValue),
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 6),
          Row(
            children: [
              const Icon(Icons.insert_drive_file_outlined,
                  size: 10, color: Color(AppColors.textTertiaryValue)),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  '${claim.docName} · p.${claim.page}',
                  style: GoogleFonts.inter(
                    fontSize: 10,
                    color: const Color(AppColors.textTertiaryValue),
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _DocumentChip extends StatelessWidget {
  final String label;

  const _DocumentChip({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(AppColors.surfaceValue),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: const Color(AppColors.borderValue)),
      ),
      child: Text(
        label,
        style: GoogleFonts.inter(
          fontSize: 10,
          color: const Color(AppColors.textSecondaryValue),
        ),
      ),
    );
  }
}

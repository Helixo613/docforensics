// lib/widgets/finding_card.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/constants.dart';
import '../models/analysis_result.dart';

enum FindingType { contradiction, agreement, uncorroborated }

// ─────────────────────────────────────────────────────────────────
// Pair card (contradiction or agreement)
// ─────────────────────────────────────────────────────────────────
class PairFindingCard extends StatefulWidget {
  final PairResult result;
  final FindingType type;
  final String? geminiInsight;
  final int index;

  const PairFindingCard({
    super.key,
    required this.result,
    required this.type,
    this.geminiInsight,
    required this.index,
  });

  @override
  State<PairFindingCard> createState() => _PairFindingCardState();
}

class _PairFindingCardState extends State<PairFindingCard>
    with SingleTickerProviderStateMixin {
  bool _expanded = false;

  Color get _accentColor => widget.type == FindingType.contradiction
      ? const Color(AppColors.contradictionColorValue)
      : const Color(AppColors.agreementColorValue);

  Color get _bgColor => widget.type == FindingType.contradiction
      ? const Color(AppColors.contradictionBgValue)
      : const Color(AppColors.agreementBgValue);

  Color get _borderColor => widget.type == FindingType.contradiction
      ? const Color(AppColors.contradictionBorderValue)
      : const Color(AppColors.agreementBorderValue);

  String get _label =>
      widget.type == FindingType.contradiction ? 'Contradiction' : 'Agreement';

  IconData get _icon => widget.type == FindingType.contradiction
      ? Icons.compare_arrows_rounded
      : Icons.handshake_outlined;

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: _expanded ? _bgColor : Colors.white,
        border: Border.all(color: _borderColor, width: 1.5),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: _accentColor.withOpacity(0.06),
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
            // Header
            InkWell(
              onTap: () => setState(() => _expanded = !_expanded),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: _accentColor.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child:
                          Icon(_icon, color: _accentColor, size: 18),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              _Chip(label: _label, color: _accentColor),
                              const SizedBox(width: 8),
                              _ConfidenceChip(
                                  confidence: widget.result.confidence),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            _previewText,
                            maxLines: _expanded ? 100 : 2,
                            overflow: _expanded
                                ? TextOverflow.visible
                                : TextOverflow.ellipsis,
                            style: GoogleFonts.inter(
                              fontSize: 13,
                              height: 1.5,
                              color:
                                  const Color(AppColors.textPrimaryValue),
                            ),
                          ),
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

            // Expanded content
            if (_expanded) ...[
              Divider(
                  height: 1,
                  color: _borderColor),
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Gemini insight
                    if (widget.geminiInsight != null) ...[
                      _InsightBox(text: widget.geminiInsight!),
                      const SizedBox(height: 16),
                    ],
                    // Claim A
                    _ClaimBlock(
                      claim: widget.result.claimA,
                      label: 'Document A',
                      accentColor: _accentColor,
                    ),
                    const SizedBox(height: 10),
                    // VS divider
                    Row(
                      children: [
                        Expanded(child: Divider(color: _borderColor)),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 12),
                          child: Text(
                            widget.type == FindingType.contradiction
                                ? 'vs'
                                : '≈',
                            style: GoogleFonts.inter(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: _accentColor,
                            ),
                          ),
                        ),
                        Expanded(child: Divider(color: _borderColor)),
                      ],
                    ),
                    const SizedBox(height: 10),
                    // Claim B
                    _ClaimBlock(
                      claim: widget.result.claimB,
                      label: 'Document B',
                      accentColor: _accentColor,
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String get _previewText {
    final a = widget.result.claimA.text;
    final b = widget.result.claimB.text;
    final connector =
        widget.type == FindingType.contradiction ? ' — contradicts — ' : ' — agrees with — ';
    return '"$a"$connector"$b"';
  }
}

// ─────────────────────────────────────────────────────────────────
// Uncorroborated card
// ─────────────────────────────────────────────────────────────────
class UncorroboratedCard extends StatefulWidget {
  final UncorroboratedResult result;
  final int index;

  const UncorroboratedCard({
    super.key,
    required this.result,
    required this.index,
  });

  @override
  State<UncorroboratedCard> createState() => _UncorroboratedCardState();
}

class _UncorroboratedCardState extends State<UncorroboratedCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    const accent = Color(AppColors.uncorroboratedColorValue);
    const bg = Color(AppColors.uncorroboratedBgValue);
    const border = Color(AppColors.uncorroboratedBorderValue);

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: _expanded ? bg : Colors.white,
        border: Border.all(color: border, width: 1.5),
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => setState(() => _expanded = !_expanded),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 28,
                height: 28,
                margin: const EdgeInsets.only(top: 1),
                decoration: BoxDecoration(
                  color: accent.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: const Icon(Icons.help_outline_rounded,
                    color: accent, size: 16),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '"${widget.result.claim.text}"',
                      maxLines: _expanded ? 100 : 2,
                      overflow: _expanded
                          ? TextOverflow.visible
                          : TextOverflow.ellipsis,
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        height: 1.5,
                        color: const Color(AppColors.textPrimaryValue),
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                    if (_expanded) ...[
                      const SizedBox(height: 10),
                      _SourceTag(
                          docName: widget.result.claim.docName,
                          page: widget.result.claim.page),
                    ],
                  ],
                ),
              ),
              Icon(
                _expanded
                    ? Icons.keyboard_arrow_up_rounded
                    : Icons.keyboard_arrow_down_rounded,
                color: const Color(AppColors.textTertiaryValue),
                size: 20,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────
// Internal sub-widgets
// ─────────────────────────────────────────────────────────────────

class _ClaimBlock extends StatelessWidget {
  final ClaimSource claim;
  final String label;
  final Color accentColor;

  const _ClaimBlock({
    required this.claim,
    required this.label,
    required this.accentColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
            color: const Color(AppColors.borderValue), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 10,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.8,
              color: const Color(AppColors.textTertiaryValue),
            ),
          ),
          const SizedBox(height: 6),
          Text(
            '"${claim.text}"',
            style: GoogleFonts.inter(
              fontSize: 13,
              height: 1.6,
              fontStyle: FontStyle.italic,
              color: const Color(AppColors.textPrimaryValue),
            ),
          ),
          const SizedBox(height: 8),
          _SourceTag(docName: claim.docName, page: claim.page),
        ],
      ),
    );
  }
}

class _SourceTag extends StatelessWidget {
  final String docName;
  final int page;

  const _SourceTag({required this.docName, required this.page});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const Icon(Icons.insert_drive_file_outlined,
            size: 12, color: Color(AppColors.textTertiaryValue)),
        const SizedBox(width: 4),
        Expanded(
          child: Text(
            '$docName · p.$page',
            style: GoogleFonts.inter(
              fontSize: 11,
              color: const Color(AppColors.textTertiaryValue),
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}

class _InsightBox extends StatelessWidget {
  final String text;

  const _InsightBox({required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(AppColors.accentValue).withOpacity(0.06),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
            color: const Color(AppColors.accentValue).withOpacity(0.2)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.auto_awesome,
              size: 14, color: Color(AppColors.accentValue)),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: GoogleFonts.inter(
                fontSize: 12,
                height: 1.5,
                color: const Color(AppColors.accentValue),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  final String label;
  final Color color;

  const _Chip({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        label.toUpperCase(),
        style: GoogleFonts.inter(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.5,
          color: color,
        ),
      ),
    );
  }
}

class _ConfidenceChip extends StatelessWidget {
  final double confidence;

  const _ConfidenceChip({required this.confidence});

  @override
  Widget build(BuildContext context) {
    final pct = (confidence * 100).toStringAsFixed(0);
    return Text(
      '$pct% confidence',
      style: GoogleFonts.inter(
        fontSize: 11,
        color: const Color(AppColors.textTertiaryValue),
      ),
    );
  }
}

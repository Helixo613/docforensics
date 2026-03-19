// lib/screens/upload_screen.dart

import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:path/path.dart' as p;
import '../config/constants.dart';
import '../services/api_service.dart';
import '../services/gemini_service.dart';
import 'results_screen.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  final _api = ApiService();
  final _gemini = GeminiService();

  List<File> _selectedFiles = [];
  bool _isLoading = false;
  String _loadingMessage = '';
  String? _errorMessage;

  // ── File picking ────────────────────────────────────────────
  Future<void> _pickFiles() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      allowMultiple: true,
    );

    if (result == null) return;

    final files = result.paths
        .whereType<String>()
        .map((path) => File(path))
        .toList();

    if (files.length > AppConfig.maxFiles) {
      setState(() => _errorMessage =
          'Maximum ${AppConfig.maxFiles} files allowed. Please remove some.');
      return;
    }

    setState(() {
      _selectedFiles = files;
      _errorMessage = null;
    });
  }

  void _removeFile(int index) {
    setState(() {
      _selectedFiles.removeAt(index);
      _errorMessage = null;
    });
  }

  // ── Analysis flow ───────────────────────────────────────────
  Future<void> _runAnalysis() async {
    if (_selectedFiles.isEmpty) {
      setState(() => _errorMessage = 'Please select at least one PDF.');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _loadingMessage = 'Uploading documents…';
    });

    try {
      setState(() => _loadingMessage = 'Analyzing with AI…');
      final result = await _api.runFullAnalysis(_selectedFiles);

      setState(() => _loadingMessage = 'Refining with Gemini…');
      final enriched = await _gemini.enrich(result);

      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => ResultsScreen(result: enriched),
        ),
      );
    } catch (e) {
      setState(() => _errorMessage = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // ── UI ──────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(AppColors.surfaceValue),
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildDropZone(),
                    if (_selectedFiles.isNotEmpty) ...[
                      const SizedBox(height: 20),
                      _buildFileList(),
                    ],
                    if (_errorMessage != null) ...[
                      const SizedBox(height: 16),
                      _buildError(),
                    ],
                    const SizedBox(height: 24),
                    _buildAnalyzeButton(),
                    const SizedBox(height: 32),
                    _buildHowItWorks(),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(24, 28, 24, 20),
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(
          bottom: BorderSide(color: Color(AppColors.borderValue)),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(AppColors.accentValue).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(
                  Icons.document_scanner_outlined,
                  color: Color(AppColors.accentValue),
                  size: 22,
                ),
              ),
              const SizedBox(width: 12),
              Text(
                'Consensus Brief',
                style: GoogleFonts.playfairDisplay(
                  fontSize: 24,
                  fontWeight: FontWeight.w700,
                  color: const Color(AppColors.textPrimaryValue),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Upload research papers to find agreements,\ncontradictions, and solo claims.',
            style: GoogleFonts.inter(
              fontSize: 13,
              height: 1.5,
              color: const Color(AppColors.textSecondaryValue),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDropZone() {
    return GestureDetector(
      onTap: _isLoading ? null : _pickFiles,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        width: double.infinity,
        height: 160,
        decoration: BoxDecoration(
          color: _selectedFiles.isEmpty
              ? Colors.white
              : const Color(AppColors.accentValue).withOpacity(0.03),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: _selectedFiles.isEmpty
                ? const Color(AppColors.borderValue)
                : const Color(AppColors.accentValue).withOpacity(0.4),
            width: 1.5,
            style: BorderStyle.solid,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              _selectedFiles.isEmpty
                  ? Icons.upload_file_outlined
                  : Icons.add_circle_outline_rounded,
              size: 36,
              color: const Color(AppColors.accentValue),
            ),
            const SizedBox(height: 12),
            Text(
              _selectedFiles.isEmpty ? 'Tap to select PDFs' : 'Tap to add more',
              style: GoogleFonts.inter(
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: const Color(AppColors.accentValue),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Up to ${AppConfig.maxFiles} PDF files · ${_selectedFiles.length}/${AppConfig.maxFiles} selected',
              style: GoogleFonts.inter(
                fontSize: 12,
                color: const Color(AppColors.textTertiaryValue),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFileList() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Selected files',
          style: GoogleFonts.inter(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.5,
            color: const Color(AppColors.textTertiaryValue),
          ),
        ),
        const SizedBox(height: 10),
        ...List.generate(
          _selectedFiles.length,
          (i) => _FileRow(
            file: _selectedFiles[i],
            onRemove: () => _removeFile(i),
          ),
        ),
      ],
    );
  }

  Widget _buildError() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(AppColors.contradictionBgValue),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
            color: const Color(AppColors.contradictionBorderValue)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline_rounded,
              size: 16, color: Color(AppColors.contradictionColorValue)),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _errorMessage!,
              style: GoogleFonts.inter(
                fontSize: 13,
                color: const Color(AppColors.contradictionColorValue),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalyzeButton() {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: _isLoading
          ? _LoadingButton(message: _loadingMessage)
          : ElevatedButton(
              onPressed:
                  _selectedFiles.isEmpty ? null : _runAnalysis,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(AppColors.accentValue),
                foregroundColor: Colors.white,
                disabledBackgroundColor:
                    const Color(AppColors.borderValue),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 0,
              ),
              child: Text(
                'Analyze Documents',
                style: GoogleFonts.inter(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
    );
  }

  Widget _buildHowItWorks() {
    const steps = [
      (Icons.upload_outlined, 'Upload', 'Select 1–5 research PDFs'),
      (Icons.hub_outlined, 'Analyze', 'Backend finds matching claims'),
      (Icons.auto_awesome, 'Refine', 'Gemini explains the findings'),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'HOW IT WORKS',
          style: GoogleFonts.inter(
            fontSize: 10,
            fontWeight: FontWeight.w700,
            letterSpacing: 1.2,
            color: const Color(AppColors.textTertiaryValue),
          ),
        ),
        const SizedBox(height: 14),
        Row(
          children: steps.map((step) {
            final isLast = step == steps.last;
            return Expanded(
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      children: [
                        Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(
                                color: const Color(AppColors.borderValue)),
                          ),
                          child: Icon(step.$1,
                              size: 18,
                              color:
                                  const Color(AppColors.textSecondaryValue)),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          step.$2,
                          style: GoogleFonts.inter(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color:
                                const Color(AppColors.textPrimaryValue),
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          step.$3,
                          style: GoogleFonts.inter(
                            fontSize: 11,
                            color:
                                const Color(AppColors.textTertiaryValue),
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                  if (!isLast)
                    const Padding(
                      padding: EdgeInsets.only(bottom: 28),
                      child: Icon(Icons.arrow_forward_ios_rounded,
                          size: 12,
                          color: Color(AppColors.textTertiaryValue)),
                    ),
                ],
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────

class _FileRow extends StatelessWidget {
  final File file;
  final VoidCallback onRemove;

  const _FileRow({required this.file, required this.onRemove});

  String get _size {
    final bytes = file.lengthSync();
    if (bytes < 1024) return '${bytes}B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)}KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)}MB';
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(AppColors.borderValue)),
      ),
      child: Row(
        children: [
          const Icon(Icons.picture_as_pdf_outlined,
              size: 18, color: Color(AppColors.contradictionColorValue)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  p.basename(file.path),
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                    color: const Color(AppColors.textPrimaryValue),
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  _size,
                  style: GoogleFonts.inter(
                    fontSize: 11,
                    color: const Color(AppColors.textTertiaryValue),
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: onRemove,
            icon: const Icon(Icons.close_rounded,
                size: 18, color: Color(AppColors.textTertiaryValue)),
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
          ),
        ],
      ),
    );
  }
}

class _LoadingButton extends StatelessWidget {
  final String message;
  const _LoadingButton({required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(AppColors.accentValue).withOpacity(0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
            color: const Color(AppColors.accentValue).withOpacity(0.3)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const SizedBox(
            width: 18,
            height: 18,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: Color(AppColors.accentValue),
            ),
          ),
          const SizedBox(width: 12),
          Text(
            message,
            style: GoogleFonts.inter(
              fontSize: 14,
              color: const Color(AppColors.accentValue),
            ),
          ),
        ],
      ),
    );
  }
}

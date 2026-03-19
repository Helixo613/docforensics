// lib/services/gemini_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/constants.dart';
import '../models/analysis_result.dart';

class GeminiService {
  final String _endpoint = AppConfig.geminiEndpoint;
  final String _apiKey = AppConfig.geminiApiKey;

  Future<String?> _generate(String prompt) async {
    if (_apiKey == 'YOUR_GEMINI_API_KEY') return null;

    try {
      final res = await http
          .post(
            Uri.parse('$_endpoint?key=$_apiKey'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'contents': [
                {
                  'parts': [
                    {'text': prompt}
                  ]
                }
              ],
              'generationConfig': {
                'temperature': 0.4,
                'maxOutputTokens': 800,
              },
            }),
          )
          .timeout(const Duration(seconds: 30));

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        return data['candidates']?[0]?['content']?['parts']?[0]?['text'];
      }
    } catch (_) {}
    return null;
  }

  /// Takes the raw AnalysisResult and enriches it with Gemini-generated
  /// readable summaries. Modifies the result in-place and returns it.
  Future<AnalysisResult> enrich(AnalysisResult result) async {
    final contradictionCount = result.contradictions.length;
    final agreementCount = result.agreements.length;
    final uncorroboratedCount = result.uncorroborated.length;

    // Build context from findings
    final contradictionContext = result.contradictions.map((c) {
      return '• "${c.claimA.text}" (${c.claimA.docName}, p.${c.claimA.page}) '
          'vs "${c.claimB.text}" (${c.claimB.docName}, p.${c.claimB.page}) '
          '[confidence: ${(c.confidence * 100).toStringAsFixed(0)}%]';
    }).join('\n');

    final agreementContext = result.agreements.map((a) {
      return '• "${a.claimA.text}" (${a.claimA.docName}) '
          'aligns with "${a.claimB.text}" (${a.claimB.docName}) '
          '[confidence: ${(a.confidence * 100).toStringAsFixed(0)}%]';
    }).join('\n');

    // ── Overall summary ───────────────────────────────────────
    final summaryPrompt = '''
You are a research analyst. Below is a structured comparison of multiple research documents.
Summarize the key takeaways in 2-3 plain English sentences. Be direct and informative.
Mention the most notable contradiction and agreement if present.

Stats: $contradictionCount contradictions, $agreementCount agreements, $uncorroboratedCount uncorroborated claims.

Contradictions:
$contradictionContext

Agreements:
$agreementContext

Write only the summary paragraph. No bullet points. No markdown.
''';

    result.geminiSummary = await _generate(summaryPrompt);

    // ── Contradiction insights ────────────────────────────────
    if (result.contradictions.isNotEmpty) {
      final insightPrompt = '''
You are a research analyst. For each contradiction below, write one plain English sentence
explaining why this disagreement matters and what it suggests.
Return ONLY a JSON array of strings like: ["insight 1", "insight 2"]

Contradictions:
$contradictionContext
''';

      final raw = await _generate(insightPrompt);
      if (raw != null) {
        try {
          final cleaned = raw
              .replaceAll('```json', '')
              .replaceAll('```', '')
              .trim();
          final list = jsonDecode(cleaned) as List;
          result.geminiContradictionInsights =
              list.map((e) => e.toString()).toList();
        } catch (_) {}
      }
    }

    // ── Agreement insights ────────────────────────────────────
    if (result.agreements.isNotEmpty) {
      final insightPrompt = '''
You are a research analyst. For each agreement below, write one plain English sentence
explaining what this consensus means and why it's significant.
Return ONLY a JSON array of strings like: ["insight 1", "insight 2"]

Agreements:
$agreementContext
''';

      final raw = await _generate(insightPrompt);
      if (raw != null) {
        try {
          final cleaned = raw
              .replaceAll('```json', '')
              .replaceAll('```', '')
              .trim();
          final list = jsonDecode(cleaned) as List;
          result.geminiAgreementInsights =
              list.map((e) => e.toString()).toList();
        } catch (_) {}
      }
    }

    return result;
  }
}

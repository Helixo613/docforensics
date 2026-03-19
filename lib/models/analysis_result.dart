// lib/models/analysis_result.dart

class HealthResponse {
  final String status;
  final bool modelsLoaded;
  final String? error;

  HealthResponse({
    required this.status,
    required this.modelsLoaded,
    this.error,
  });

  factory HealthResponse.fromJson(Map<String, dynamic> json) {
    return HealthResponse(
      status: json['status'] ?? 'unknown',
      modelsLoaded: json['models_loaded'] ?? false,
      error: json['error'],
    );
  }

  bool get isReady => status == 'ok' && modelsLoaded;
}

// ─────────────────────────────────────────────

class DocumentSummary {
  final String name;
  final int pages;
  final int sentences;

  DocumentSummary({
    required this.name,
    required this.pages,
    required this.sentences,
  });

  factory DocumentSummary.fromJson(Map<String, dynamic> json) {
    return DocumentSummary(
      name: json['name'] ?? '',
      pages: json['pages'] ?? 0,
      sentences: json['sentences'] ?? 0,
    );
  }
}

class UploadResponse {
  final String sessionId;
  final List<DocumentSummary> documents;
  final int totalSentences;

  UploadResponse({
    required this.sessionId,
    required this.documents,
    required this.totalSentences,
  });

  factory UploadResponse.fromJson(Map<String, dynamic> json) {
    return UploadResponse(
      sessionId: json['session_id'] ?? '',
      documents: (json['documents'] as List<dynamic>?)
              ?.map((d) => DocumentSummary.fromJson(d))
              .toList() ??
          [],
      totalSentences: json['total_sentences'] ?? 0,
    );
  }
}

// ─────────────────────────────────────────────

class ResultStats {
  final int totalSentences;
  final int candidatePairs;
  final int agreementsFound;
  final int contradictionsFound;
  final int uncorroboratedCount;

  ResultStats({
    required this.totalSentences,
    required this.candidatePairs,
    required this.agreementsFound,
    required this.contradictionsFound,
    required this.uncorroboratedCount,
  });

  factory ResultStats.fromJson(Map<String, dynamic> json) {
    return ResultStats(
      totalSentences: json['total_sentences'] ?? 0,
      candidatePairs: json['candidate_pairs'] ?? 0,
      agreementsFound: json['agreements_found'] ?? 0,
      contradictionsFound: json['contradictions_found'] ?? 0,
      uncorroboratedCount: json['uncorroborated_count'] ?? 0,
    );
  }
}

class ClaimSource {
  final String text;
  final String docName;
  final int page;

  ClaimSource({
    required this.text,
    required this.docName,
    required this.page,
  });

  factory ClaimSource.fromJson(Map<String, dynamic> json) {
    return ClaimSource(
      text: json['text'] ?? '',
      docName: json['doc_name'] ?? '',
      page: json['page'] ?? 0,
    );
  }
}

class PairResult {
  final String id;
  final ClaimSource claimA;
  final ClaimSource claimB;
  final double confidence;

  PairResult({
    required this.id,
    required this.claimA,
    required this.claimB,
    required this.confidence,
  });

  factory PairResult.fromJson(Map<String, dynamic> json) {
    return PairResult(
      id: json['id'] ?? '',
      claimA: ClaimSource.fromJson(json['claim_a'] ?? {}),
      claimB: ClaimSource.fromJson(json['claim_b'] ?? {}),
      confidence: (json['confidence'] ?? 0.0).toDouble(),
    );
  }
}

class UncorroboratedResult {
  final String id;
  final ClaimSource claim;

  UncorroboratedResult({
    required this.id,
    required this.claim,
  });

  factory UncorroboratedResult.fromJson(Map<String, dynamic> json) {
    return UncorroboratedResult(
      id: json['id'] ?? '',
      claim: ClaimSource.fromJson(json['claim'] ?? {}),
    );
  }
}

class AnalysisResult {
  final String sessionId;
  final ResultStats stats;
  final List<PairResult> contradictions;
  final List<PairResult> agreements;
  final List<UncorroboratedResult> uncorroborated;
  final bool isDemoData;

  // Gemini-refined summaries (set after Gemini processing)
  String? geminiSummary;
  List<String>? geminiContradictionInsights;
  List<String>? geminiAgreementInsights;

  AnalysisResult({
    required this.sessionId,
    required this.stats,
    required this.contradictions,
    required this.agreements,
    required this.uncorroborated,
    this.isDemoData = false,
    this.geminiSummary,
    this.geminiContradictionInsights,
    this.geminiAgreementInsights,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json,
      {bool isDemoData = false}) {
    return AnalysisResult(
      sessionId: json['session_id'] ?? '',
      stats: ResultStats.fromJson(json['stats'] ?? {}),
      contradictions: (json['contradictions'] as List<dynamic>?)
              ?.map((c) => PairResult.fromJson(c))
              .toList() ??
          [],
      agreements: (json['agreements'] as List<dynamic>?)
              ?.map((a) => PairResult.fromJson(a))
              .toList() ??
          [],
      uncorroborated: (json['uncorroborated'] as List<dynamic>?)
              ?.map((u) => UncorroboratedResult.fromJson(u))
              .toList() ??
          [],
      isDemoData: isDemoData,
    );
  }
}

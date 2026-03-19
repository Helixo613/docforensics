// lib/models/session_results.dart

import 'analysis_result.dart';
import 'v2_models.dart';

class SessionResults {
  final AnalysisResult v1;
  final IssueMapResponse? v2;

  SessionResults({
    required this.v1,
    this.v2,
  });
}

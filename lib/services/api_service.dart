// lib/services/api_service.dart

import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../config/constants.dart';
import '../models/analysis_result.dart';

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}

class ApiService {
  final String _base = AppConfig.backendBaseUrl;

  // ── GET /health ──────────────────────────────────────────
  Future<HealthResponse> checkHealth() async {
    try {
      final res = await http
          .get(Uri.parse('$_base/health'))
          .timeout(const Duration(seconds: 10));

      if (res.statusCode == 200) {
        return HealthResponse.fromJson(jsonDecode(res.body));
      }
      return HealthResponse(status: 'error', modelsLoaded: false);
    } catch (_) {
      return HealthResponse(status: 'error', modelsLoaded: false);
    }
  }

  // ── POST /upload ─────────────────────────────────────────
  Future<UploadResponse> uploadFiles(List<File> files) async {
    final uri = Uri.parse('$_base/upload');
    final request = http.MultipartRequest('POST', uri);

    for (final file in files) {
      request.files.add(await http.MultipartFile.fromPath('files', file.path));
    }

    try {
      final streamed = await request.send().timeout(
            Duration(seconds: AppConfig.uploadTimeoutSeconds),
          );
      final body = await streamed.stream.bytesToString();

      if (streamed.statusCode == 200) {
        return UploadResponse.fromJson(jsonDecode(body));
      }
      throw ApiException('Upload failed (${streamed.statusCode}): $body');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Upload error: $e');
    }
  }

  // ── POST /analyze/{session_id} ────────────────────────────
  Future<AnalysisResult> analyze(String sessionId) async {
    try {
      final res = await http
          .post(Uri.parse('$_base/analyze/$sessionId'))
          .timeout(Duration(seconds: AppConfig.analyzeTimeoutSeconds));

      if (res.statusCode == 200) {
        return AnalysisResult.fromJson(jsonDecode(res.body));
      }
      throw ApiException('Analysis failed (${res.statusCode})');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Analysis error: $e');
    }
  }

  // ── GET /results/{session_id} ─────────────────────────────
  Future<AnalysisResult> getResults(String sessionId) async {
    try {
      final res = await http
          .get(Uri.parse('$_base/results/$sessionId'))
          .timeout(Duration(seconds: AppConfig.analyzeTimeoutSeconds));

      if (res.statusCode == 200) {
        return AnalysisResult.fromJson(jsonDecode(res.body));
      }
      throw ApiException('Results fetch failed (${res.statusCode})');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Results error: $e');
    }
  }

  // ── GET /demo ─────────────────────────────────────────────
  Future<AnalysisResult> getDemo() async {
    try {
      final res = await http
          .get(Uri.parse('$_base/demo'))
          .timeout(const Duration(seconds: 15));

      if (res.statusCode == 200) {
        return AnalysisResult.fromJson(jsonDecode(res.body), isDemoData: true);
      }
      throw ApiException('Demo fetch failed (${res.statusCode})');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Demo error: $e');
    }
  }

  // ── Full flow: upload → analyze → fallback to demo ────────
  Future<AnalysisResult> runFullAnalysis(List<File> files) async {
    try {
      final upload = await uploadFiles(files);
      final result = await analyze(upload.sessionId);
      return result;
    } catch (_) {
      // Fallback to demo
      try {
        return await getDemo();
      } catch (e) {
        throw ApiException('Both backend and demo failed: $e');
      }
    }
  }
}

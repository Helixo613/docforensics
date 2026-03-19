// lib/config/constants.dart

class AppConfig {
  // ── Replace with your actual backend URL ──
  static const String backendBaseUrl = 'http://localhost:8000';

  // ── Replace with your Gemini API key ──
  static const String geminiApiKey = 'YOUR_GEMINI_API_KEY';

  static const String geminiEndpoint =
      'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent';

  static const int uploadTimeoutSeconds = 60;
  static const int analyzeTimeoutSeconds = 120;
  static const int maxFiles = 5;
}

class AppColors {
  // Contradiction — warm coral
  static const int contradictionColorValue = 0xFFE53935;
  static const int contradictionBgValue = 0xFFFFF5F5;
  static const int contradictionBorderValue = 0xFFFFCDD2;

  // Agreement — sage green
  static const int agreementColorValue = 0xFF2E7D32;
  static const int agreementBgValue = 0xFFF1F8E9;
  static const int agreementBorderValue = 0xFFC8E6C9;

  // Uncorroborated — warm amber
  static const int uncorroboratedColorValue = 0xFFF57F17;
  static const int uncorroboratedBgValue = 0xFFFFFDE7;
  static const int uncorroboratedBorderValue = 0xFFFFF9C4;

  // Neutrals
  static const int surfaceValue = 0xFFFAF9F7;
  static const int cardValue = 0xFFFFFFFF;
  static const int borderValue = 0xFFE8E4DE;
  static const int textPrimaryValue = 0xFF1A1714;
  static const int textSecondaryValue = 0xFF6B6560;
  static const int textTertiaryValue = 0xFF9C9690;
  static const int accentValue = 0xFF2D5BE3;
}

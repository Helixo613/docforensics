// lib/main.dart

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'config/constants.dart';
import 'screens/upload_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );
  runApp(const ConsensusBriefApp());
}

class ConsensusBriefApp extends StatelessWidget {
  const ConsensusBriefApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Consensus Brief',
      debugShowCheckedModeBanner: false,
      theme: _buildTheme(),
      home: const UploadScreen(),
    );
  }

  ThemeData _buildTheme() {
    final base = ThemeData.light(useMaterial3: true);
    return base.copyWith(
      scaffoldBackgroundColor: const Color(AppColors.surfaceValue),
      colorScheme: base.colorScheme.copyWith(
        primary: const Color(AppColors.accentValue),
        surface: const Color(AppColors.surfaceValue),
      ),
      textTheme: GoogleFonts.interTextTheme(base.textTheme),
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0.5,
        titleTextStyle: GoogleFonts.playfairDisplay(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: const Color(AppColors.textPrimaryValue),
        ),
        iconTheme: const IconThemeData(
          color: Color(AppColors.textSecondaryValue),
        ),
      ),
      tabBarTheme: TabBarThemeData(
        indicatorColor: const Color(AppColors.accentValue),
        labelColor: const Color(AppColors.textPrimaryValue),
        unselectedLabelColor: const Color(AppColors.textTertiaryValue),
        labelStyle:
            GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600),
        unselectedLabelStyle:
            GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w400),
      ),
      dividerTheme: const DividerThemeData(
        color: Color(AppColors.borderValue),
        thickness: 1,
        space: 0,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(AppColors.accentValue),
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 0,
        ),
      ),
    );
  }
}

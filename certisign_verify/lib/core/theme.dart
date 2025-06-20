import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color primaryColor = Color(0xFF2E8B57); // Vert SeaGreen
  static const Color primaryLightColor = Color(0xFF3CB371); // MediumSeaGreen
  static const Color primaryDarkColor = Color(0xFF1E5E3A); // Vert foncé
  static const Color accentColor = Color(0xFF4CAF50); // Vert plus vif
  static const Color accentLightColor = Color(0xFF81C784); // Vert clair
  static const Color accentDarkColor = Color(0xFF388E3C); // Vert moyen-foncé
  
  static const Color successColor = Color(0xFF4CAF50);
  static const Color warningColor = Color(0xFFFFB74D);
  static const Color dangerColor = Color(0xFFF44336);
  
  static const Color textColor = Color(0xFF333333);
  static const Color textSecondaryColor = Color(0xFF666666);
  static const Color textLightColor = Color(0xFFFFFFFF);
  
  static const Color backgroundColor = Color(0xFFF8F9FA);
  static const Color backgroundLightColor = Color(0xFFFFFFFF);
  static const Color backgroundDarkColor = Color(0xFFE9ECEF);
  static const Color borderColor = Color(0xFFCED4DA);
  
  static const Color cardBackgroundColor = Color(0xFFFFFFFF);
  static const Color appBarBackgroundColor = Color(0xFFF8F9FA);

  // Dark Theme Colors
  static const Color darkPrimaryColor = Color(0xFF3CB371);
  static const Color darkPrimaryLightColor = Color(0xFF4FD487);
  static const Color darkPrimaryDarkColor = Color(0xFF2A7D53);
  static const Color darkAccentColor = Color(0xFF66BB6A);
  static const Color darkAccentLightColor = Color(0xFF81C784);
  static const Color darkAccentDarkColor = Color(0xFF43A047);
  
  static const Color darkTextColor = Color(0xFFE0E0E0);
  static const Color darkTextSecondaryColor = Color(0xFFBBBBBB);
  
  static const Color darkBackgroundColor = Color(0xFF212529);
  static const Color darkBackgroundLightColor = Color(0xFF343A40);
  static const Color darkBackgroundDarkColor = Color(0xFF1A1D20);
  static const Color darkBorderColor = Color(0xFF495057);
  
  static const Color darkCardBackgroundColor = Color(0xFF343A40);
  static const Color darkAppBarBackgroundColor = Color(0xFF212529);

  // Shadows
  static List<BoxShadow> lightShadow = [
    BoxShadow(
      color: Colors.black.withOpacity(0.05),
      blurRadius: 4,
      offset: const Offset(0, 2),
    ),
  ];
  
  static List<BoxShadow> mediumShadow = [
    BoxShadow(
      color: Colors.black.withOpacity(0.1),
      blurRadius: 8,
      offset: const Offset(0, 4),
    ),
  ];
  
  static List<BoxShadow> largeShadow = [
    BoxShadow(
      color: Colors.black.withOpacity(0.15),
      blurRadius: 16,
      offset: const Offset(0, 8),
    ),
  ];

  // Dark mode shadows
  static List<BoxShadow> darkLightShadow = [
    BoxShadow(
      color: Colors.black.withOpacity(0.2),
      blurRadius: 4,
      offset: const Offset(0, 2),
    ),
  ];
  
  static List<BoxShadow> darkMediumShadow = [
    BoxShadow(
      color: Colors.black.withOpacity(0.3),
      blurRadius: 8,
      offset: const Offset(0, 4),
    ),
  ];
  
  static List<BoxShadow> darkLargeShadow = [
    BoxShadow(
      color: Colors.black.withOpacity(0.4),
      blurRadius: 16,
      offset: const Offset(0, 8),
    ),
  ];

  // Light Theme
  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.light(
      primary: primaryColor,
      secondary: accentColor,
      surface: backgroundLightColor,
      error: dangerColor,
      onPrimary: textLightColor,
      onSecondary: textLightColor,
      onSurface: textColor,
      onError: textLightColor,
      brightness: Brightness.light,
    ),
    scaffoldBackgroundColor: backgroundColor,
    appBarTheme: const AppBarTheme(
      color: appBarBackgroundColor,
      elevation: 0,
      iconTheme: IconThemeData(color: textColor),
      titleTextStyle: TextStyle(
        color: textColor, 
        fontSize: 20, 
        fontWeight: FontWeight.bold,
      ),
    ),
    cardTheme: CardTheme(
      color: cardBackgroundColor,
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryColor,
        foregroundColor: textLightColor,
        elevation: 2,
        padding: const EdgeInsets.symmetric(
          horizontal: 20, 
          vertical: 12,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: primaryColor,
        side: const BorderSide(color: primaryColor),
        padding: const EdgeInsets.symmetric(
          horizontal: 20, 
          vertical: 12,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: primaryColor,
        padding: const EdgeInsets.symmetric(
          horizontal: 16, 
          vertical: 8,
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: backgroundLightColor,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: borderColor),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: borderColor),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: primaryColor, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: dangerColor),
      ),
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 16, 
        vertical: 16,
      ),
    ),
    textTheme: GoogleFonts.robotoTextTheme(
      const TextTheme(
        displayLarge: TextStyle(
          color: textColor, 
          fontWeight: FontWeight.bold,
        ),
        displayMedium: TextStyle(color: textColor),
        displaySmall: TextStyle(color: textColor),
        headlineLarge: TextStyle(color: textColor),
        headlineMedium: TextStyle(color: textColor),
        headlineSmall: TextStyle(color: textColor),
        titleLarge: TextStyle(
          color: textColor, 
          fontWeight: FontWeight.bold,
        ),
        titleMedium: TextStyle(color: textColor),
        titleSmall: TextStyle(color: textColor),
        bodyLarge: TextStyle(color: textColor),
        bodyMedium: TextStyle(color: textColor),
        bodySmall: TextStyle(color: textSecondaryColor),
        labelLarge: TextStyle(color: textColor),
        labelMedium: TextStyle(color: textColor),
        labelSmall: TextStyle(color: textSecondaryColor),
      ),
    ),
    iconTheme: const IconThemeData(color: primaryColor),
  );

  // Dark Theme
  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.dark(
      primary: darkPrimaryColor,
      secondary: darkAccentColor,
      surface: darkBackgroundLightColor,
      error: dangerColor,
      onPrimary: textLightColor,
      onSecondary: textLightColor,
      onSurface: darkTextColor,
      onError: textLightColor,
      brightness: Brightness.dark,
    ),
    scaffoldBackgroundColor: darkBackgroundColor,
    appBarTheme: const AppBarTheme(
      color: darkAppBarBackgroundColor,
      elevation: 0,
      iconTheme: IconThemeData(color: darkTextColor),
      titleTextStyle: TextStyle(
        color: darkTextColor, 
        fontSize: 20, 
        fontWeight: FontWeight.bold,
      ),
    ),
    cardTheme: CardTheme(
      color: darkCardBackgroundColor,
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: darkPrimaryColor,
        foregroundColor: textLightColor,
        elevation: 2,
        padding: const EdgeInsets.symmetric(
          horizontal: 20, 
          vertical: 12,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: darkPrimaryColor,
        side: const BorderSide(color: darkPrimaryColor),
        padding: const EdgeInsets.symmetric(
          horizontal: 20, 
          vertical: 12,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: darkPrimaryColor,
        padding: const EdgeInsets.symmetric(
          horizontal: 16, 
          vertical: 8,
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: darkBackgroundLightColor,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: darkBorderColor),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: darkBorderColor),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: darkPrimaryColor, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: dangerColor),
      ),
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 16, 
        vertical: 16,
      ),
    ),
    textTheme: GoogleFonts.robotoTextTheme(
      const TextTheme(
        displayLarge: TextStyle(
          color: darkTextColor, 
          fontWeight: FontWeight.bold,
        ),
        displayMedium: TextStyle(color: darkTextColor),
        displaySmall: TextStyle(color: darkTextColor),
        headlineLarge: TextStyle(color: darkTextColor),
        headlineMedium: TextStyle(color: darkTextColor),
        headlineSmall: TextStyle(color: darkTextColor),
        titleLarge: TextStyle(
          color: darkTextColor, 
          fontWeight: FontWeight.bold,
        ),
        titleMedium: TextStyle(color: darkTextColor),
        titleSmall: TextStyle(color: darkTextColor),
        bodyLarge: TextStyle(color: darkTextColor),
        bodyMedium: TextStyle(color: darkTextColor),
        bodySmall: TextStyle(color: darkTextSecondaryColor),
        labelLarge: TextStyle(color: darkTextColor),
        labelMedium: TextStyle(color: darkTextColor),
        labelSmall: TextStyle(color: darkTextSecondaryColor),
      ),
    ),
    iconTheme: const IconThemeData(color: darkPrimaryColor),
  );
}

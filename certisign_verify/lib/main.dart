import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';

import 'core/theme.dart';
import 'features/history/verification_history.dart';
import 'features/home/home_screen.dart';
import 'features/history/history_screen.dart';
import 'features/scan/scan_screen.dart';
import 'shared/theme_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Optimisations de performance
  await _performAppOptimizations();
  
  // Initialiser l'historique en parallèle si possible
  final historyInit = VerificationHistory.instance.initialize();
  
  // Définir l'orientation portrait uniquement
  final orientationInit = SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  // Attendre que les initialisations essentielles soient terminées
  await Future.wait([historyInit, orientationInit]);
  
  runApp(const CertiSignVerifyApp());
}

/// Optimisations de performance pour l'application
Future<void> _performAppOptimizations() async {
  // Réduire la complexité de rendu pour améliorer les performances
  await SystemChrome.setEnabledSystemUIMode(
    SystemUiMode.edgeToEdge,
    overlays: [SystemUiOverlay.top],
  );
  
  // Améliorer les performances de rendu
  PaintingBinding.instance.imageCache.maximumSizeBytes = 10 * 1024 * 1024; // Limiter à 10MB
  
  // Optimiser la performance réseau (optionnel)
  // HttpClient().maxConnectionsPerHost = 8; // Si nous faisons beaucoup d'appels réseau

  // Configuration d'Impeller (si disponible)
  if (const bool.fromEnvironment('dart.vm.product')) {
    // Optimisations en mode production uniquement
    debugPrint = (String? message, {int? wrapWidth}) {}; // Désactiver les logs en prod
  }
}

class CertiSignVerifyApp extends StatelessWidget {
  const CertiSignVerifyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => ThemeProvider(),
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, _) {
          return MaterialApp(
            debugShowCheckedModeBanner: false,
            title: 'CertiSign Verify',
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: themeProvider.themeMode,
            localizationsDelegates: const [
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            supportedLocales: const [
              Locale('fr'),
              Locale('en'),
            ],
            locale: const Locale('fr'),
            home: const MainScreen(),
          );
        },
      ),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;
  
  final List<Widget> _screens = [
    const HomeScreen(),
    const HistoryScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    // Définir le style de la barre d'état du téléphone
    SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Theme.of(context).brightness == Brightness.dark
          ? Brightness.light
          : Brightness.dark,
    ));
    
    return Scaffold(
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 500),
        transitionBuilder: (Widget child, Animation<double> animation) {
          return FadeTransition(
            opacity: animation,
            child: SlideTransition(
              position: Tween<Offset>(
                begin: const Offset(0.05, 0),
                end: Offset.zero,
              ).animate(animation),
              child: child,
            ),
          );
        },
        child: _screens[_currentIndex],
      ),
      extendBody: true, // Important pour que le corps s'étende sous la nav bar
      floatingActionButton: _buildScanButton(context),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      bottomNavigationBar: _buildBottomNavigationBar(context),
    );
  }
  
  // Barre de navigation compacte style pill-nav
  Widget _buildBottomNavigationBar(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    
    return Container(
      height: 64, // Hauteur réduite
      margin: const EdgeInsets.fromLTRB(24, 0, 24, 16), // Marge augmentée horizontalement
      decoration: BoxDecoration(
        color: isDarkMode 
            ? Colors.grey.shade900.withOpacity(0.8) 
            : Colors.grey.shade200.withOpacity(0.8),
        borderRadius: BorderRadius.circular(32), // Pill shape
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(isDarkMode ? 0.25 : 0.1),
            blurRadius: 10,
            spreadRadius: 0,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(32),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Bouton Accueil
                _buildNavPill(
                  icon: Icons.home_outlined,
                  activeIcon: Icons.home_rounded,
                  label: 'Accueil',
                  index: 0,
                ),
                
                // Espace au milieu pour le bouton flottant
                const SizedBox(width: 16),
                
                // Bouton Historique
                _buildNavPill(
                  icon: Icons.history_outlined,
                  activeIcon: Icons.history_rounded,
                  label: 'Historique',
                  index: 1,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  // Pill navigation button
  Widget _buildNavPill({
    required IconData icon,
    required IconData activeIcon,
    required String label,
    required int index,
  }) {
    final isSelected = index == _currentIndex;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = AppTheme.primaryColor;
    
    return Expanded(
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () {
            HapticFeedback.selectionClick();
            setState(() {
              _currentIndex = index;
            });
          },
          borderRadius: BorderRadius.circular(24),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            padding: const EdgeInsets.symmetric(vertical: 8),
            decoration: BoxDecoration(
              color: isSelected
                  ? primaryColor.withOpacity(isDarkMode ? 0.3 : 0.25)
                  : Colors.transparent,
              borderRadius: BorderRadius.circular(24),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  isSelected ? activeIcon : icon,
                  color: isSelected 
                      ? isDarkMode ? Colors.white : primaryColor
                      : isDarkMode ? Colors.white70 : Colors.black54,
                  size: 22, // Taille réduite
                ),
                if (isSelected) ...[  
                  const SizedBox(width: 8),
                  Text(
                    label,
                    style: TextStyle(
                      color: isDarkMode ? Colors.white : primaryColor,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  // Bouton de scan central avec animation de pulsation
  Widget _buildScanButton(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppTheme.primaryColor,
            Color.lerp(AppTheme.primaryColor, Colors.blue, 0.4) ?? AppTheme.primaryColor,
          ],
        ),
        borderRadius: BorderRadius.circular(28),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.4),
            blurRadius: 12,
            spreadRadius: 2,
            offset: const Offset(0, 4),
          ),
          BoxShadow(
            color: Colors.white.withOpacity(0.2),
            blurRadius: 8,
            spreadRadius: -2,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () {
            HapticFeedback.lightImpact();
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => const ScanScreen(),
              ),
            );
          },
          customBorder: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(28),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Icon(
              Icons.qr_code_scanner_rounded,
              color: Colors.white,
              size: 28,
            ),
          ),
        ),
      ),
    )
    .animate()
    .fadeIn(duration: const Duration(milliseconds: 500))
    .then()
    .scale(
      begin: const Offset(1.0, 1.0),
      end: const Offset(1.05, 1.05),
      duration: const Duration(seconds: 1),
      curve: Curves.easeInOut,
    )
    .then()
    .scale(
      begin: const Offset(1.05, 1.05),
      end: const Offset(1.0, 1.0),
      duration: const Duration(seconds: 1),
      curve: Curves.easeInOut,
    )
    .then();
  }


}

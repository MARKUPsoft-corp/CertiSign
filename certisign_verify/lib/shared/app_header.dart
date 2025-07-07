import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../shared/theme_provider.dart';

class AppHeader extends StatelessWidget {
  final String? title;
  final bool showBackButton;
  final bool showThemeToggle;
  final VoidCallback? onBackPressed;

  const AppHeader({
    super.key,
    this.title,
    this.showBackButton = false,
    this.showThemeToggle = true,
    this.onBackPressed,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    // Configurer la barre d'état pour qu'elle soit transparente avec du contenu clair
    SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent, // Transparent pour laisser voir l'en-tête
      statusBarIconBrightness: Brightness.light, // Icônes claires sur fond sombre
      statusBarBrightness: Brightness.dark, // Pour iOS
    ));

    return Container(
      // Étendre jusqu'à la status bar
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: MediaQuery.of(context).padding.top + 12, // Padding du top + status bar
        bottom: 12,
      ),
      decoration: BoxDecoration(
        // Toujours sombre peu importe le thème
        color: const Color(0xFF1A1A1A), // Fond toujours sombre
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 8,
            spreadRadius: 0,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Bouton retour OU Logo Doc@uthANTIC
          if (showBackButton)
            Row(
              children: [
                IconButton(
                  icon: const Icon(
                    Icons.arrow_back,
                    color: Colors.white,
                    size: 24,
                  ),
                  onPressed: onBackPressed ?? () => Navigator.of(context).pop(),
                ),
                if (title != null) ...[
                  const SizedBox(width: 8),
                  Flexible(
                    child: Text(
                      title!,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ],
            )
          else
            // Logo Doc@uthANTIC
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.2),
                        blurRadius: 4,
                        spreadRadius: 0,
                      ),
                    ],
                  ),
                  child: Image.asset(
                    'assets/images/doc.png',
                    width: 24,
                    height: 24,
                  ),
                ),
                const SizedBox(width: 8),
                RichText(
                  text: const TextSpan(
                    children: [
                      TextSpan(
                        text: 'Doc',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF00A651), // Vert
                        ),
                      ),
                      TextSpan(
                        text: '@uth',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFFE74C3C), // Rouge
                        ),
                      ),
                      TextSpan(
                        text: 'ANTIC',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFFF1C40F), // Jaune
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

          // Basculer le thème - toujours en couleur claire pour être visible sur fond sombre
          if (showThemeToggle)
            IconButton(
              icon: Icon(
                isDarkMode ? Icons.wb_sunny : Icons.nightlight_round,
                color: isDarkMode
                    ? Colors.amber.shade300 // Couleur dorée en mode sombre
                    : Colors.white, // Blanc en mode clair pour contraster avec le fond sombre
                size: 24,
              ),
              onPressed: () {
                final themeProvider = Provider.of<ThemeProvider>(
                  context,
                  listen: false,
                );
                themeProvider.toggleTheme();
              },
            )
          else
            const SizedBox(width: 48), // Espace pour équilibrer
        ],
      ),
    );
  }
} 
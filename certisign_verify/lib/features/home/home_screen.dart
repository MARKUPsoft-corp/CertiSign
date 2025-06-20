import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:provider/provider.dart';

import '../../core/theme.dart';
import '../../shared/animated_particles.dart';
import '../../shared/theme_provider.dart';
import '../scan/scan_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Fond avec particules animées optimisées
          const Positioned.fill(
            child: AnimatedParticles(
              particleCount: 6, // Encore réduit pour optimiser le démarrage
              opacity: 0.15, // Moins visible = moins coûteux en rendu
              maxSize: 3, // Taille réduite pour meilleure performance
            ),
          ),

          // Fond avec gradient subtil
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Theme.of(context).colorScheme.surface,
                    Theme.of(context).colorScheme.surface.withOpacity(0.8),
                  ],
                ),
              ),
            ),
          ),

          // Contenu principal
          SafeArea(
            child: Column(
              children: [
                _buildHeader(context),
                Expanded(
                  child: SingleChildScrollView(
                    physics: const BouncingScrollPhysics(),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const SizedBox(height: 20),
                          _buildHeroSection(context),
                          const SizedBox(height: 40),
                          _buildFeaturesHighlightSection(context),
                          const SizedBox(height: 40),
                          _buildFeatureSection(context),
                          const SizedBox(height: 40),
                          _buildSecuritySection(context),
                          const SizedBox(height: 40),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Theme.of(context).appBarTheme.backgroundColor,
        boxShadow: isDarkMode ? AppTheme.darkLightShadow : AppTheme.lightShadow,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Logo
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color:
                      isDarkMode
                          ? AppTheme.darkPrimaryColor
                          : AppTheme.primaryColor,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  FontAwesomeIcons.shieldHalved,
                  color: AppTheme.textLightColor,
                  size: 16,
                ),
              ),
              const SizedBox(width: 8),
              RichText(
                text: TextSpan(
                  children: [
                    TextSpan(
                      text: 'Certi',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color:
                            isDarkMode
                                ? AppTheme.darkPrimaryColor
                                : AppTheme.primaryColor,
                      ),
                    ),
                    TextSpan(text: ' ', style: const TextStyle(fontSize: 20)),
                    WidgetSpan(
                      child: Icon(
                        FontAwesomeIcons.check,
                        size: 14,
                        color:
                            isDarkMode
                                ? AppTheme.darkAccentColor
                                : AppTheme.accentColor,
                      ),
                    ),
                    TextSpan(
                      text: 'Sign',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color:
                            isDarkMode
                                ? AppTheme.darkAccentColor
                                : AppTheme.accentColor,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          // Basculer le thème
          IconButton(
            icon: Icon(
              isDarkMode ? Icons.wb_sunny : Icons.nightlight_round,
              color:
                  isDarkMode
                      ? AppTheme.darkPrimaryColor
                      : AppTheme.primaryColor,
            ),
            onPressed: () {
              final themeProvider = Provider.of<ThemeProvider>(
                context,
                listen: false,
              );
              themeProvider.toggleTheme();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildHeroSection(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).colorScheme.primary;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 30, horizontal: 20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            primaryColor.withOpacity(isDarkMode ? 0.15 : 0.08),
            Colors.transparent,
          ],
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: primaryColor.withOpacity(isDarkMode ? 0.1 : 0.05),
            blurRadius: 20,
            spreadRadius: 0,
          ),
        ],
        border: Border.all(color: primaryColor.withOpacity(0.12), width: 1),
      ),
      child: Column(
        children: [
          // Titre élégant centré
          Container(
            margin: const EdgeInsets.only(bottom: 20),
            child: Column(
              children: [
                Text(
                      'VÉRIFICATION DE',
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        letterSpacing: 3,
                        color: primaryColor.withOpacity(0.8),
                      ),
                    )
                    .animate()
                    .fadeIn(duration: 500.ms, delay: 100.ms)
                    .slideY(begin: -0.2, end: 0),

                const SizedBox(height: 10),

                Text(
                      'SIGNATURES ÉLECTRONIQUES',
                      textAlign: TextAlign.center,
                      style: Theme.of(
                        context,
                      ).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.2,
                        color: primaryColor,
                      ),
                    )
                    .animate()
                    .fadeIn(duration: 500.ms, delay: 300.ms)
                    .slideY(begin: -0.1, end: 0),

                const SizedBox(height: 20),

                Container(
                      width: 80,
                      height: 4,
                      decoration: BoxDecoration(
                        color: primaryColor,
                        borderRadius: BorderRadius.circular(2),
                        boxShadow: [
                          BoxShadow(
                            color: primaryColor.withOpacity(0.3),
                            blurRadius: 4,
                            spreadRadius: 0,
                          ),
                        ],
                      ),
                    )
                    .animate()
                    .fadeIn(duration: 400.ms, delay: 400.ms)
                    .scale(
                      begin: const Offset(0.5, 1),
                      end: const Offset(1, 1),
                    ),
              ],
            ),
          ),

          // Sous-titre
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 10),
            child: Text(
              'Scannez et vérifiez l\'authenticité de vos documents en toute confiance',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                height: 1.5,
                color: Theme.of(
                  context,
                ).textTheme.bodyLarge?.color?.withOpacity(0.8),
              ),
            ).animate().fadeIn(duration: 400.ms, delay: 500.ms),
          ),

          const SizedBox(height: 32),

          // Bouton d'action
          SizedBox(
            width: double.infinity,
            child: _buildActionButton(
                  context: context,
                  icon: FontAwesomeIcons.qrcode,
                  label: 'Scanner un QR Code',
                  onTap:
                      () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const ScanScreen(),
                        ),
                      ),
                )
                .animate()
                .fadeIn(duration: 400.ms, delay: 700.ms)
                .scale(
                  begin: const Offset(0.95, 0.95),
                  end: const Offset(1, 1),
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureSection(BuildContext context) {
    final primaryColor = Theme.of(context).colorScheme.primary;

    return Column(
      children: [
        // Titre de section centré et stylé
        Container(
          margin: const EdgeInsets.symmetric(vertical: 20),
          child: Column(
            children: [
              Text(
                'COMMENT ÇA MARCHE',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                  color: primaryColor,
                ),
              ).animate().fadeIn(duration: 400.ms, delay: 300.ms),

              const SizedBox(height: 12),

              // Ligne décorative centrée
              Center(
                child: Container(
                      width: 80,
                      height: 4,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            primaryColor.withOpacity(0.1),
                            primaryColor,
                            primaryColor.withOpacity(0.1),
                          ],
                        ),
                        borderRadius: BorderRadius.circular(2),
                        boxShadow: [
                          BoxShadow(
                            color: primaryColor.withOpacity(0.3),
                            blurRadius: 3,
                            spreadRadius: 0,
                          ),
                        ],
                      ),
                    )
                    .animate()
                    .fadeIn(duration: 400.ms, delay: 200.ms)
                    .scale(
                      begin: const Offset(0.5, 1),
                      end: const Offset(1, 1),
                    ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 30),

        // Timeline centrale avec étapes
        Stack(
          children: [
            // Ligne verticale centrale (en arrière-plan)
            Positioned.fill(
              child: Align(
                alignment: Alignment.center,
                child: Container(
                      width: 3,
                      height: 380, // Hauteur ajustable selon le contenu
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            primaryColor.withOpacity(0.2),
                            primaryColor,
                            primaryColor.withOpacity(0.2),
                          ],
                        ),
                        borderRadius: BorderRadius.circular(1.5),
                      ),
                    )
                    .animate()
                    .fadeIn(duration: 600.ms, delay: 100.ms)
                    .custom(
                      duration: 800.ms,
                      delay: 100.ms,
                      begin: 0.0,
                      end: 1.0,
                      builder:
                          (context, value, child) => SizedBox(
                            width: 3,
                            height: 380 * value,
                            child: child,
                          ),
                    ),
              ),
            ),

            // Étapes
            Column(
              children: [
                // Étape 1
                _buildHowItWorksStepNew(
                  context: context,
                  number: 1,
                  title: 'Scannez le QR Code',
                  description:
                      'Utilisez l\'appareil photo de votre téléphone pour scanner le code QR présent sur le document signé.',
                  icon: FontAwesomeIcons.qrcode,
                  delay: 100,
                ),

                const SizedBox(height: 40),

                // Étape 2
                _buildHowItWorksStepNew(
                  context: context,
                  number: 2,
                  title: 'Vérification Automatique',
                  description:
                      'L\'application analyse la signature cryptographique et vérifie son authenticité en temps réel.',
                  icon: FontAwesomeIcons.shieldHalved,
                  delay: 300,
                ),

                const SizedBox(height: 40),

                // Étape 3
                _buildHowItWorksStepNew(
                  context: context,
                  number: 3,
                  title: 'Résultat Instantané',
                  description:
                      'Obtenez immédiatement le résultat de la vérification avec toutes les informations sur la signature.',
                  icon: FontAwesomeIcons.circleCheck,
                  delay: 500,
                ),
              ],
            ),
          ],
        ),
      ],
    );
  }

  // Nouvelle méthode pour créer les étapes du processus avec le numéro au dessus
  Widget _buildHowItWorksStepNew({
    required BuildContext context,
    required int number,
    required String title,
    required String description,
    required IconData icon,
    required int delay,
  }) {
    final primaryColor = Theme.of(context).colorScheme.primary;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Contenu principal
            Container(
              constraints: const BoxConstraints(maxWidth: 320),
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  // Box principale
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(24),
                    margin: const EdgeInsets.only(top: 25),
                    decoration: BoxDecoration(
                      color:
                          isDarkMode
                              ? Color.lerp(
                                    Colors.grey.shade900,
                                    primaryColor,
                                    0.05,
                                  ) ??
                                  Colors.grey.shade900.withOpacity(0.5)
                              : Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: primaryColor.withOpacity(0.2),
                        width: 1.5,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(
                            isDarkMode ? 0.2 : 0.05,
                          ),
                          blurRadius: 20,
                          offset: const Offset(0, 8),
                          spreadRadius: 0,
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Titre et icône
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            // Icône
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: primaryColor.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Icon(icon, color: primaryColor, size: 20),
                            ),
                            const SizedBox(width: 16),

                            // Titre
                            Expanded(
                              child: Text(
                                title,
                                style: Theme.of(
                                  context,
                                ).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  letterSpacing: 0.2,
                                ),
                              ),
                            ),
                          ],
                        ),

                        const SizedBox(height: 16),

                        // Description
                        Text(
                          description,
                          style: Theme.of(
                            context,
                          ).textTheme.bodyMedium?.copyWith(
                            height: 1.5,
                            letterSpacing: 0.2,
                            color: isDarkMode ? Colors.white70 : Colors.black87,
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Numéro d'étape au-dessus
                  Positioned(
                    top: 0,
                    left: 0,
                    right: 0,
                    child: Center(
                      child: Container(
                            width: 50,
                            height: 50,
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                                colors: [
                                  primaryColor,
                                  Color.lerp(primaryColor, Colors.blue, 0.3) ??
                                      primaryColor,
                                ],
                              ),
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: primaryColor.withOpacity(0.4),
                                  blurRadius: 8,
                                  offset: const Offset(0, 4),
                                  spreadRadius: 0,
                                ),
                              ],
                              border: Border.all(
                                color:
                                    isDarkMode ? Colors.black12 : Colors.white,
                                width: 3,
                              ),
                            ),
                            child: Center(
                              child: Text(
                                number.toString(),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 22,
                                ),
                              ),
                            ),
                          )
                          .animate()
                          .fadeIn(duration: 500.ms, delay: delay.ms)
                          .scale(
                            begin: const Offset(0.7, 0.7),
                            end: const Offset(1, 1),
                          ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        )
        .animate()
        .fadeIn(duration: 600.ms, delay: (delay + 100).ms)
        .slideY(begin: 0.1, end: 0);
  }

  Widget _buildFeatureItem({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String description,
  }) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).colorScheme.primary;

    return Container(
      margin: const EdgeInsets.only(bottom: 28),
      width: double.infinity,
      decoration: BoxDecoration(
        color:
            isDarkMode
                ? Color.lerp(Colors.grey.shade900, primaryColor, 0.05) ??
                    Colors.grey.shade900.withOpacity(0.5)
                : Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(isDarkMode ? 0.2 : 0.06),
            blurRadius: 20,
            offset: const Offset(0, 8),
            spreadRadius: 0,
          ),
        ],
        border: Border.all(color: primaryColor.withOpacity(0.12), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // En-tête avec dégradé
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 18),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  isDarkMode
                      ? primaryColor.withOpacity(0.15)
                      : primaryColor.withOpacity(0.1),
                  isDarkMode
                      ? primaryColor.withOpacity(0.05)
                      : primaryColor.withOpacity(0.02),
                ],
              ),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(23),
                topRight: Radius.circular(23),
              ),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Icône dans un cercle dégradé
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        primaryColor,
                        Color.lerp(primaryColor, Colors.blue, 0.3) ??
                            primaryColor,
                      ],
                    ),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: primaryColor.withOpacity(0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 4),
                        spreadRadius: 0,
                      ),
                    ],
                  ),
                  child: Icon(icon, color: Colors.white, size: 22),
                ),
                const SizedBox(width: 18),

                // Titre
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.2,
                      color: primaryColor,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Description
          Padding(
            padding: const EdgeInsets.all(24),
            child: Text(
              description,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                height: 1.5,
                letterSpacing: 0.2,
                color: isDarkMode ? Colors.white70 : Colors.black87,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeaturesHighlightSection(BuildContext context) {
    final primaryColor = Theme.of(context).colorScheme.primary;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        // Titre de section centré et stylé
        Container(
          margin: const EdgeInsets.symmetric(vertical: 20),
          child: Column(
            children: [
              Text(
                'FONCTIONNALITÉS CLÉS',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                  color: primaryColor,
                ),
              ).animate().fadeIn(duration: 400.ms, delay: 300.ms),

              const SizedBox(height: 12),

              // Ligne décorative centrée
              Center(
                child: Container(
                      width: 60,
                      height: 3,
                      decoration: BoxDecoration(
                        color: primaryColor,
                        borderRadius: BorderRadius.circular(1.5),
                        boxShadow: [
                          BoxShadow(
                            color: primaryColor.withOpacity(0.3),
                            blurRadius: 3,
                            spreadRadius: 0,
                          ),
                        ],
                      ),
                    )
                    .animate()
                    .fadeIn(duration: 400.ms, delay: 200.ms)
                    .scale(
                      begin: const Offset(0.5, 1),
                      end: const Offset(1, 1),
                    ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 24),

        _buildFeatureItem(
              context: context,
              icon: FontAwesomeIcons.qrcode,
              title: 'Scanner Avancé',
              description:
                  'Lecture rapide et précise des QR codes contenant des signatures électroniques.',
            )
            .animate()
            .fadeIn(duration: 500.ms, delay: 300.ms)
            .slideY(begin: 0.1, end: 0),

        _buildFeatureItem(
              context: context,
              icon: FontAwesomeIcons.shieldHalved,
              title: 'Vérification Cryptographique',
              description:
                  'Analyse sécurisée des signatures avec algorithmes RSA et hachage SHA-256.',
            )
            .animate()
            .fadeIn(duration: 500.ms, delay: 400.ms)
            .slideY(begin: 0.1, end: 0),

        _buildFeatureItem(
              context: context,
              icon: FontAwesomeIcons.clockRotateLeft,
              title: 'Historique des Vérifications',
              description:
                  'Consultez l\'historique de toutes vos vérifications précédentes avec leur statut.',
            )
            .animate()
            .fadeIn(duration: 500.ms, delay: 500.ms)
            .slideY(begin: 0.1, end: 0),
      ],
    );
  }

  Widget _buildSecuritySection(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).colorScheme.primary;

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors:
              isDarkMode
                  ? [
                    Color.lerp(Colors.grey.shade900, primaryColor, 0.08) ??
                        Colors.grey.shade900,
                    Color.lerp(
                          Colors.grey.shade800,
                          Colors.blue.shade900,
                          0.12,
                        ) ??
                        Colors.grey.shade800,
                  ]
                  : [
                    Color.lerp(Colors.white, primaryColor, 0.03) ??
                        Colors.white,
                    Color.lerp(Colors.white, Colors.blue, 0.05) ?? Colors.white,
                  ],
        ),
        borderRadius: BorderRadius.circular(30),
        boxShadow: [
          BoxShadow(
            color: primaryColor.withOpacity(isDarkMode ? 0.2 : 0.1),
            blurRadius: 20,
            offset: const Offset(0, 10),
            spreadRadius: 0,
          ),
        ],
        border: Border.all(color: primaryColor.withOpacity(0.2), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // En-tête avec dégradé
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  primaryColor,
                  Color.lerp(primaryColor, Colors.blue, 0.5) ?? primaryColor,
                ],
              ),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(28),
                topRight: Radius.circular(28),
              ),
              boxShadow: [
                BoxShadow(
                  color: primaryColor.withOpacity(0.3),
                  blurRadius: 10,
                  offset: const Offset(0, 2),
                  spreadRadius: 0,
                ),
              ],
            ),
            child: Row(
              children: [
                // Icône de bouclier dans un cercle lumineux
                Container(
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.15),
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.white.withOpacity(0.1),
                            blurRadius: 12,
                            spreadRadius: 0,
                          ),
                        ],
                        border: Border.all(
                          color: Colors.white.withOpacity(0.3),
                          width: 2,
                        ),
                      ),
                      child: Center(
                        child: Icon(
                          FontAwesomeIcons.shieldHalved,
                          color: Colors.white,
                          size: 28,
                        ),
                      ),
                    )
                    .animate()
                    .fadeIn(duration: 600.ms, delay: 100.ms)
                    .scale(
                      begin: const Offset(0.8, 0.8),
                      end: const Offset(1, 1),
                    ),

                const SizedBox(width: 20),

                // Titre de la section
                Expanded(
                  child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Sécurité de niveau entreprise',
                            style: Theme.of(
                              context,
                            ).textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Vérification cryptographique avancée',
                            style: Theme.of(
                              context,
                            ).textTheme.bodyMedium?.copyWith(
                              color: Colors.white.withOpacity(0.9),
                              letterSpacing: 0.3,
                            ),
                          ),
                        ],
                      )
                      .animate()
                      .fadeIn(duration: 500.ms, delay: 200.ms)
                      .slideY(begin: -0.2, end: 0),
                ),
              ],
            ),
          ),

          // Corps de la section
          Padding(
            padding: const EdgeInsets.all(28.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Chez CertiSign, nous prenons la sécurité de vos documents très au sérieux. Notre application mobile utilise des algorithmes cryptographiques avancés pour garantir l\'authenticité des signatures électroniques.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    height: 1.5,
                    letterSpacing: 0.2,
                  ),
                ).animate().fadeIn(duration: 500.ms, delay: 300.ms),

                const SizedBox(height: 24),

                // Grille de fonctionnalités de sécurité (2x2)
                Row(
                  children: [
                    Expanded(
                      child: _buildSecurityFeatureNew(
                        context: context,
                        icon: FontAwesomeIcons.key,
                        feature: 'Vérification RSA',
                        delay: 400,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildSecurityFeatureNew(
                        context: context,
                        icon: FontAwesomeIcons.lock,
                        feature: 'Hachage SHA-256',
                        delay: 500,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                Row(
                  children: [
                    Expanded(
                      child: _buildSecurityFeatureNew(
                        context: context,
                        icon: FontAwesomeIcons.fileContract,
                        feature: 'Conforme Loi n°2010/021',
                        delay: 600,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildSecurityFeatureNew(
                        context: context,
                        icon: FontAwesomeIcons.userShield,
                        feature: 'Protection des données',
                        delay: 700,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 500.ms, delay: 100.ms).slideY(begin: 0.05, end: 0);
  }

  Widget _buildSecurityFeatureNew({
    required BuildContext context,
    required IconData icon,
    required String feature,
    required int delay,
  }) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).colorScheme.primary;

    return Container(
          height: 120, // Augmentation de la hauteur
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
          decoration: BoxDecoration(
            color:
                isDarkMode
                    ? Color.lerp(Colors.grey.shade800, primaryColor, 0.05) ??
                        Colors.grey.shade800.withOpacity(0.5)
                    : Colors.white.withOpacity(0.5),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: primaryColor.withOpacity(0.15), width: 1),
            boxShadow: [
              BoxShadow(
                color: primaryColor.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 4),
                spreadRadius: 0,
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Icône de la fonctionnalité
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      primaryColor,
                      Color.lerp(primaryColor, Colors.blue, 0.4) ??
                          primaryColor,
                    ],
                  ),
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: primaryColor.withOpacity(0.2),
                      blurRadius: 6,
                      offset: const Offset(0, 3),
                      spreadRadius: 0,
                    ),
                  ],
                ),
                child: Center(child: Icon(icon, color: Colors.white, size: 18)),
              ),

              const SizedBox(height: 8), // Réduit pour gagner de la place
              // Texte de la fonctionnalité
              Expanded(
                child: Center(
                  child: Text(
                    feature,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                      fontSize: 11, // Réduit pour mieux s'adapter
                      height: 1.2, // Espacement des lignes plus serré
                      color: isDarkMode ? Colors.white : Colors.black87,
                    ),
                    overflow: TextOverflow.fade,
                    maxLines: 3, // Augmentation du nombre de lignes
                  ),
                ),
              ),
            ],
          ),
        )
        .animate()
        .fadeIn(duration: 400.ms, delay: delay.ms)
        .scale(begin: const Offset(0.95, 0.95), end: const Offset(1, 1));
  }

  Widget _buildActionButton({
    required BuildContext context,
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    final primaryColor = Theme.of(context).colorScheme.primary;

    return Container(
      width: double.infinity,
      height: 60,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            primaryColor,
            Color.lerp(primaryColor, Colors.blue, 0.3) ?? primaryColor,
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: primaryColor.withOpacity(0.4),
            blurRadius: 20,
            offset: const Offset(0, 8),
            spreadRadius: -5,
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          splashColor: Colors.white.withOpacity(0.1),
          highlightColor: Colors.white.withOpacity(0.05),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, color: Colors.white, size: 22),
                const SizedBox(width: 16),
                Text(
                  label,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.5,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

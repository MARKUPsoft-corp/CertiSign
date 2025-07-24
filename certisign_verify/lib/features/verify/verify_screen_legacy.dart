import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:intl/intl.dart';

import '../../shared/app_header.dart';
import '../../utils/document_preview_utils.dart';
import '../history/verification_history.dart';
import '../../shared/animated_particles.dart';

class VerifyScreenLegacy extends StatefulWidget {
  final String documentId;
  final Map<String, dynamic> verificationResult;
  
  const VerifyScreenLegacy({
    super.key,
    required this.documentId,
    required this.verificationResult,
  });

  @override
  State<VerifyScreenLegacy> createState() => _VerifyScreenLegacyState();
}

class _VerifyScreenLegacyState extends State<VerifyScreenLegacy> {
  bool _isVerifying = true;
  bool _isVerified = false;
  String? _errorMessage;
  String _documentTitle = 'Document vérifié';
  String? _originalDocumentBase64;
  
  @override
  void initState() {
    super.initState();
    _processVerificationResult();
  }
  
  Future<void> _processVerificationResult() async {
    try {
      print('Traitement du résultat de vérification legacy: ${widget.verificationResult.keys}');
      
      // Afficher l'animation de vérification durant un court instant
      await Future.delayed(const Duration(milliseconds: 1000));
      
      // Extraire les données du résultat de vérification
      final isValid = widget.verificationResult['valid'] as bool? ?? false;
      print('Document valide: $isValid');
      
      String documentTitle = 'Document non identifié';
      
      // Extraire le titre du document
      if (widget.verificationResult.containsKey('api_response') && 
          widget.verificationResult['api_response'] != null) {
        final apiResponse = widget.verificationResult['api_response'] as Map<String, dynamic>;
        
        if (apiResponse.containsKey('original_filename')) {
          documentTitle = apiResponse['original_filename'] as String;
        }
        
        // Récupérer le document en base64
        if (apiResponse.containsKey('original_document')) {
          final originalDoc = apiResponse['original_document'];
          if (originalDoc is String) {
            _originalDocumentBase64 = originalDoc;
          }
        }
      }
      
      // Si pas de document dans api_response, essayer dans le niveau principal
      if (_originalDocumentBase64 == null && 
          widget.verificationResult.containsKey('original_document_base64')) {
        _originalDocumentBase64 = widget.verificationResult['original_document_base64'] as String?;
      }
      
      // Mettre à jour l'interface
      setState(() {
        _isVerifying = false;
        _isVerified = isValid;
        _documentTitle = documentTitle;
        
        if (!isValid) {
          if (widget.verificationResult.containsKey('message')) {
            final message = widget.verificationResult['message'];
            if (message is String) {
              _errorMessage = message;
            } else {
              _errorMessage = message.toString();
            }
          } else {
            _errorMessage = 'La signature ne correspond pas au document original.';
          }
        }
      });
      
      // Ajouter à l'historique
      final historyEntry = VerificationHistoryEntry(
        timestamp: DateTime.now(),
        signatureDate: DateTime.now(), // Date de vérification comme date de signature
        isVerified: isValid,
        qrData: {
          'document_id': widget.documentId,
          'verification_result': {
            'valid': isValid,
            'document_id': widget.documentId,
            'verification_date': DateTime.now().toIso8601String(),
            'document_title': documentTitle,
          },
        },
      );
      
      try {
        VerificationHistory.instance.addVerification(historyEntry);
      } catch (e) {
        print('Erreur lors de l\'ajout à l\'historique: $e');
      }
      
    } catch (e) {
      setState(() {
        _isVerifying = false;
        _isVerified = false;
        _errorMessage = 'Erreur lors de la vérification: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    
    return Scaffold(
      body: Column(
        children: [
          // En-tête sombre uniforme avec bouton retour
          AppHeader(
            title: 'VÉRIFICATION LEGACY',
            showBackButton: true,
          ),
          
          // Contenu principal
          Expanded(
            child: Stack(
              children: [
                // Fond avec particules pour cohérence visuelle
                const Positioned.fill(
                  child: AnimatedParticles(
                    particleCount: 6,
                    opacity: 0.15,
                    maxSize: 3,
                  ),
                ),

                // Fond avec gradient
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

                // Contenu scrollable
                SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      children: [
                        _isVerifying
                            ? _buildVerificationInProgress(isDarkMode)
                            : _buildVerificationResult(isDarkMode),
                      ],
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
  
  Widget _buildVerificationInProgress(bool isDarkMode) {
    final primaryColor = Theme.of(context).colorScheme.primary;

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 30, horizontal: 24),
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
              // Icône animée de sécurité
              Icon(
                FontAwesomeIcons.shield, 
                size: 48,
                color: primaryColor.withOpacity(0.7),
              )
              .animate(onPlay: (controller) => controller.repeat(reverse: true))
              .scale(begin: const Offset(1.0, 1.0), end: const Offset(1.1, 1.1), duration: 1500.ms),
              
              const SizedBox(height: 30),
              
              Text(
                'VÉRIFICATION EN COURS',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  letterSpacing: 2,
                  color: primaryColor,
                ),
              )
              .animate()
              .fadeIn(duration: 500.ms, delay: 100.ms)
              .move(delay: 100.ms, duration: 500.ms, begin: const Offset(0, -15), curve: Curves.easeOutQuad),
              
              const SizedBox(height: 20),
              
              Container(
                width: 80,
                height: 4,
                decoration: BoxDecoration(
                  color: primaryColor.withOpacity(0.6),
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
              .fadeIn(duration: 500.ms, delay: 200.ms)
              .slideX(begin: -0.2, end: 0),
              
              const SizedBox(height: 20),
              
              Text(
                'Vérification de l\'authenticité du document avec le système legacy. Cette opération ne prendra que quelques instants...',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  height: 1.5,
                ),
              )
              .animate()
              .fadeIn(duration: 500.ms, delay: 300.ms),
              
              const SizedBox(height: 40),
              
              SizedBox(
                width: 60,
                height: 60,
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(primaryColor),
                  strokeWidth: 3,
                ),
              )
              .animate()
              .fadeIn(duration: 800.ms, delay: 500.ms),
            ],
          ),
        ),
      ],
    );
  }
  
  Widget _buildVerificationResult(bool isDarkMode) {
    final colorScheme = Theme.of(context).colorScheme;
    
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(vertical: 24),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Résumé de la vérification
            Animate(
              effects: [
                FadeEffect(duration: const Duration(milliseconds: 400)),
                SlideEffect(
                  begin: const Offset(0, 0.1),
                  end: const Offset(0, 0),
                  duration: const Duration(milliseconds: 400),
                ),
              ],
              child: _buildVerificationSummary(isDarkMode),
            ),
            
            // Informations basiques du document
            const SizedBox(height: 32),
            
            Animate(
              effects: [
                FadeEffect(
                  duration: const Duration(milliseconds: 400),
                  delay: const Duration(milliseconds: 100),
                ),
              ],
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 6),
                decoration: BoxDecoration(
                  border: Border(
                    bottom: BorderSide(color: colorScheme.primary.withOpacity(0.2), width: 2),
                    left: BorderSide(color: colorScheme.primary.withOpacity(0.7), width: 4),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(FontAwesomeIcons.fileShield, 
                         color: colorScheme.primary, 
                         size: 20),
                    const SizedBox(width: 10),
                    Text(
                      'INFORMATIONS DU DOCUMENT',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: colorScheme.primary,
                        letterSpacing: 0.8,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // ID du document
            _buildDetailItem(
              isDarkMode: isDarkMode,
              icon: FontAwesomeIcons.idCard,
              title: 'ID du document',
              value: widget.documentId,
              delay: 200,
            ),
            
            // Nom du document
            _buildDetailItem(
              isDarkMode: isDarkMode,
              icon: FontAwesomeIcons.fileLines,
              title: 'Nom du fichier',
              value: _documentTitle,
              delay: 250,
            ),
            
            // Date de vérification
            _buildDetailItem(
              isDarkMode: isDarkMode,
              icon: FontAwesomeIcons.calendarDays,
              title: 'Date de vérification',
              value: DateFormat('dd/MM/yyyy à HH:mm').format(DateTime.now()),
              delay: 300,
            ),
            
            // Document Preview (si disponible)
            if (_originalDocumentBase64 != null) ...[              
              const SizedBox(height: 32),
              
              // Titre de la section aperçu du document
              Animate(
                effects: [
                  FadeEffect(
                    duration: const Duration(milliseconds: 400),
                    delay: const Duration(milliseconds: 350),
                  ),
                ],
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 6),
                  decoration: BoxDecoration(
                    border: Border(
                      bottom: BorderSide(color: colorScheme.primary.withOpacity(0.2), width: 2),
                      left: BorderSide(color: colorScheme.primary.withOpacity(0.7), width: 4),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(FontAwesomeIcons.filePdf, 
                           color: colorScheme.primary, 
                           size: 20),
                      const SizedBox(width: 10),
                      Text(
                        'DOCUMENT ORIGINAL',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: colorScheme.primary,
                          letterSpacing: 0.8,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 16),
              
              Animate(
                effects: [
                  FadeEffect(
                    duration: const Duration(milliseconds: 500),
                    delay: const Duration(milliseconds: 400),
                  ),
                ],
                child: _buildDocumentPreview(isDarkMode),
              ),
            ],
            
            const SizedBox(height: 32),
            
            // Bouton d'action
            Animate(
              effects: [
                FadeEffect(
                  duration: const Duration(milliseconds: 400),
                  delay: const Duration(milliseconds: 600),
                ),
              ],
              child: Row(
                children: [
                  Expanded(
                    child: Container(
                      height: 56,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(16),
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            Theme.of(context).colorScheme.primary,
                            Color.lerp(Theme.of(context).colorScheme.primary, Colors.blue, 0.3) ?? 
                                Theme.of(context).colorScheme.primary,
                          ],
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Theme.of(context).colorScheme.primary.withOpacity(0.4),
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
                          onTap: () => Navigator.of(context).pop(),
                          splashColor: Colors.white.withOpacity(0.1),
                          highlightColor: Colors.white.withOpacity(0.05),
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 24),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(FontAwesomeIcons.qrcode, color: Colors.white, size: 22),
                                const SizedBox(width: 16),
                                const Text(
                                  'Scanner un autre QR',
                                  style: TextStyle(
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
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildVerificationSummary(bool isDarkMode) {
    final colorScheme = Theme.of(context).colorScheme;
    final successColor = const Color(0xFF61DEA4);
    final errorColor = const Color(0xFFFF5F6D);
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 32, horizontal: 24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            _isVerified
                ? successColor.withOpacity(isDarkMode ? 0.25 : 0.15)
                : errorColor.withOpacity(isDarkMode ? 0.25 : 0.15),
            _isVerified
                ? successColor.withOpacity(0.0)
                : errorColor.withOpacity(0.0),
          ],
        ),
        borderRadius: BorderRadius.circular(28),
        boxShadow: [
          BoxShadow(
            color: _isVerified
                ? successColor.withOpacity(isDarkMode ? 0.25 : 0.15)
                : errorColor.withOpacity(isDarkMode ? 0.25 : 0.15),
            blurRadius: 24,
            spreadRadius: 0,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(
          color: _isVerified
              ? successColor.withOpacity(isDarkMode ? 0.4 : 0.3)
              : errorColor.withOpacity(isDarkMode ? 0.4 : 0.3),
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Icône animée dans un cercle avec effet de lueur
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: (_isVerified ? successColor : errorColor).withOpacity(0.1),
              boxShadow: [
                BoxShadow(
                  color: (_isVerified ? successColor : errorColor).withOpacity(0.25),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: Icon(
              _isVerified
                  ? FontAwesomeIcons.circleCheck
                  : FontAwesomeIcons.circleXmark,
              size: 40,
              color: _isVerified ? successColor : errorColor,
            ),
          ).animate(onPlay: (controller) => controller.repeat(reverse: true, period: const Duration(seconds: 3)))
            .scale(begin: const Offset(1.0, 1.0), end: const Offset(1.05, 1.05)),
          
          const SizedBox(height: 28),
          
          // Titre du résultat
          Text(
            _isVerified ? 'DOCUMENT AUTHENTIQUE' : 'DOCUMENT NON AUTHENTIQUE',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.2,
                  color: _isVerified ? successColor : errorColor,
                ),
          ),
          
          const SizedBox(height: 16),
          
          // Titre du document si disponible
          if (_documentTitle.isNotEmpty && _documentTitle != 'Document non identifié')
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Text(
                _documentTitle,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: colorScheme.onSurface.withOpacity(0.9),
                ),
              ),
            ),
          
          const SizedBox(height: 8),
          
          // Message du résultat
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            child: Text(
              _isVerified
                  ? 'Le document a été vérifié avec succès via le système legacy. Son authenticité est confirmée.'
                  : _errorMessage ?? 'La vérification du document a échoué. Le document pourrait ne pas être authentique.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                height: 1.5,
                color: colorScheme.onSurface.withOpacity(0.9),
              ),
            ),
          ),
        ],
      ),
    ).animate()
      .fadeIn(duration: 600.ms, delay: 100.ms)
      .move(delay: 200.ms, duration: 600.ms, begin: const Offset(0, 15), end: const Offset(0, 0), curve: Curves.easeOutQuint);
  }

  Widget _buildDetailItem({
    required bool isDarkMode,
    required IconData icon,
    required String title,
    required String value,
    required int delay,
  }) {
    final cardBgColor = isDarkMode
        ? const Color(0xFF22272E)
        : const Color(0xFFF7F9FC);
    
    final titleColor = isDarkMode
        ? Colors.grey[300]
        : Colors.grey[800];
        
    final primaryColor = Theme.of(context).colorScheme.primary;
        
    return Animate(
      effects: [
        FadeEffect(
          duration: const Duration(milliseconds: 400),
          delay: Duration(milliseconds: delay),
        ),
        SlideEffect(
          begin: const Offset(0, 0.1),
          end: const Offset(0, 0),
          duration: const Duration(milliseconds: 400),
          delay: Duration(milliseconds: delay),
        ),
      ],
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 10),
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 18),
        decoration: BoxDecoration(
          color: cardBgColor,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: isDarkMode
                  ? Colors.black.withOpacity(0.3)
                  : Colors.grey.withOpacity(0.1),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // En-tête avec icône et titre
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 18),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    primaryColor.withOpacity(0.12),
                    primaryColor.withOpacity(0.05),
                  ],
                ),
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  topRight: Radius.circular(16),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: primaryColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(
                      icon,
                      color: primaryColor,
                      size: 18,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Text(
                      title,
                      style: TextStyle(
                        color: titleColor,
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // Contenu de valeur
            Container(
              padding: const EdgeInsets.all(24),
              width: double.infinity,
              child: Text(
                value,
                style: TextStyle(
                  color: isDarkMode
                      ? Colors.grey[300]
                      : Colors.grey[700],
                  fontSize: 15,
                  height: 1.4,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  /// Construit un aperçu du document PDF à partir des données base64
  Widget _buildDocumentPreview(bool isDarkMode) {
    final colorScheme = Theme.of(context).colorScheme;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                'Document original',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: colorScheme.primary,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            // Bouton pour agrandir la prévisualisation
            IconButton(
              icon: const Icon(FontAwesomeIcons.expand),
              onPressed: () => _showFullDocumentPreview(),
              tooltip: 'Agrandir',
              style: IconButton.styleFrom(
                foregroundColor: colorScheme.primary,
                backgroundColor: colorScheme.primary.withOpacity(0.1),
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 20),
        
        Container(
          width: double.infinity,
          height: 320,
          decoration: BoxDecoration(
            color: colorScheme.surface,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: colorScheme.shadow.withOpacity(0.15),
                blurRadius: 24,
                spreadRadius: 1,
                offset: const Offset(0, 4),
              ),
            ],
            border: Border.all(
              color: colorScheme.primary.withOpacity(0.18),
              width: 1.5,
            ),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(15),
            child: Stack(
              alignment: Alignment.center,
              children: [
                // Affichage du document PDF
                if (_originalDocumentBase64 != null)
                  DocumentPreviewUtils.renderDocumentPreview(
                    context, 
                    _originalDocumentBase64!, 
                    _documentTitle,
                    _isVerified,
                  ),
                
                // Superposition d'un effet de papier
                Positioned.fill(
                  child: IgnorePointer(
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            Colors.white.withOpacity(0.1),
                            Colors.transparent,
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
                
                // Filigrane de vérification si le document est authentique
                if (_isVerified)
                  Positioned(
                    bottom: 20,
                    right: 20,
                    child: Opacity(
                      opacity: 0.18,
                      child: Transform.rotate(
                        angle: -0.2,
                        child: Text(
                          'DOC@UTHANTIC VÉRIFIÉ',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                        ),
                      ),
                    ),
                  ),
                
                // Bouton pour télécharger le document
                Positioned(
                  bottom: 16,
                  right: 16,
                  child: Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: colorScheme.primary,
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: [
                        BoxShadow(
                          color: colorScheme.primary.withOpacity(0.3),
                          blurRadius: 10,
                          spreadRadius: 0,
                        ),
                      ],
                    ),
                    child: IconButton(
                      icon: const Icon(
                        FontAwesomeIcons.download,
                        size: 20,
                        color: Colors.white,
                      ),
                      onPressed: () {
                        if (_originalDocumentBase64 != null) {
                          DocumentPreviewUtils.saveDocument(
                            context,
                            _originalDocumentBase64!,
                            _documentTitle,
                          );
                        } else {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Document non disponible'),
                              duration: Duration(seconds: 2),
                              backgroundColor: Colors.orange,
                            ),
                          );
                        }
                      },
                    ),
                  ),
                ),
                
                // Bouton pour voir le document en plein écran
                Positioned(
                  bottom: 16,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: TextButton.icon(
                      onPressed: () => _showFullDocumentPreview(),
                      icon: const Icon(FontAwesomeIcons.fileShield, size: 18),
                      label: const Text('Voir le document'),
                      style: TextButton.styleFrom(
                        backgroundColor: Colors.white.withOpacity(0.9),
                        foregroundColor: Colors.green.shade700,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 10,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
  
  /// Affiche le document en plein écran
  void _showFullDocumentPreview() {
    if (_originalDocumentBase64 == null) return;
    
    DocumentPreviewUtils.showFullDocumentPreview(
      context,
      _originalDocumentBase64!,
      _documentTitle,
      _isVerified,
    );
  }
} 
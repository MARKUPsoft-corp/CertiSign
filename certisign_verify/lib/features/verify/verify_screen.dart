import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:intl/intl.dart';

import '../../shared/app_header.dart';
import '../../utils/document_preview_utils.dart';
import '../history/verification_history.dart';
import '../../shared/animated_particles.dart';

// Extension pour faciliter l'accès aux animations
extension AnimateWidgetExtension on Widget {
  // Cette extension n'est pas utilisée mais montre comment on pourrait faire
  Widget animateWithFade({Duration? duration, Duration? delay}) {
    return Animate(
      effects: [
        FadeEffect(
          duration: duration ?? const Duration(milliseconds: 500),
          delay: delay,
        ),
      ],
      child: this,
    );
  }
}

class VerifyScreen extends StatefulWidget {
  final String documentId;
  final Map<String, dynamic> verificationResult;
  final Map<String, dynamic>? qrData;
  
  const VerifyScreen({
    super.key,
    required this.documentId,
    required this.verificationResult,
    this.qrData,
  });

  @override
  State<VerifyScreen> createState() => _VerifyScreenState();
}

class _VerifyScreenState extends State<VerifyScreen> {
  bool _isVerifying = true;
  bool _isVerified = false;
  String? _errorMessage;
  DateTime? _signatureDate;
  String _documentTitle = 'Document vérifié';
  String? _originalDocumentBase64;
  
  // 🆕 Variables pour les signatures éphémères
  bool _isExpired = false;
  String? _signatureType;
  DateTime? _expirationDate;
  
  @override
  void initState() {
    super.initState();
    _processVerificationResult();
  }
  
  Future<void> _processVerificationResult() async {
    try {
      print('Traitement du résultat de vérification: ${widget.verificationResult.keys}');
      
      // Afficher l'animation de vérification durant un court instant
      await Future.delayed(const Duration(milliseconds: 1000));
      
      // Extraire les données du résultat de vérification
        final isValid = widget.verificationResult['valid'] as bool? ?? false;
      print('Document valide: $isValid');
      
      String documentTitle = 'Document non identifié';
      
      // Extraire la date de signature et d'autres informations 
      if (widget.verificationResult.containsKey('verification_info') && 
          widget.verificationResult['verification_info'] != null) {
        
        final verificationInfo = widget.verificationResult['verification_info'] as Map<String, dynamic>;
        
        if (verificationInfo.containsKey('signature_date')) {
          try {
            _signatureDate = DateTime.parse(verificationInfo['signature_date'] as String);
            print('Date de signature: $_signatureDate');
          } catch (e) {
            print('Erreur de parsing de la date: $e');
          }
        }
        
        if (verificationInfo.containsKey('document_title')) {
          documentTitle = verificationInfo['document_title'] as String;
        }
      }
      
      // Traiter le nouveau format d'API
      if (widget.verificationResult.containsKey('api_response')) {
        final apiResponse = widget.verificationResult['api_response'] as Map<String, dynamic>;
        
        // Extraire le nom du document
        if (apiResponse.containsKey('original_filename')) {
          documentTitle = apiResponse['original_filename'] as String;
        }
        
        // Extraire la date de signature
        if (apiResponse.containsKey('signature_date') && _signatureDate == null) {
          try {
            _signatureDate = DateTime.parse(apiResponse['signature_date'] as String);
          } catch (e) {
            print('Erreur de parsing de la date API: $e');
          }
        }
        
        // 🆕 Traiter les informations de signature éphémère
        if (apiResponse.containsKey('signature_type')) {
          _signatureType = apiResponse['signature_type'] as String?;
          print('Type de signature: $_signatureType');
        }
        
        if (apiResponse.containsKey('expiration_date')) {
          try {
            _expirationDate = DateTime.parse(apiResponse['expiration_date'] as String);
            print('Date d\'expiration: $_expirationDate');
          } catch (e) {
            print('Erreur de parsing de la date d\'expiration: $e');
          }
        }
        
        if (apiResponse.containsKey('is_expired')) {
          _isExpired = apiResponse['is_expired'] as bool? ?? false;
          print('Document expiré: $_isExpired');
        }
        
        // Récupérer le document original en base64 si disponible (sauf si expiré)
        if (apiResponse.containsKey('original_document') && !_isExpired) {
          // Vérifier le type avant de faire la conversion
          final originalDoc = apiResponse['original_document'];
          if (originalDoc is String) {
            _originalDocumentBase64 = originalDoc;
          } else if (originalDoc is Map) {
            // Dans le cas où original_document est un objet avec content_b64
            try {
              final Map<String, dynamic> docMap = originalDoc as Map<String, dynamic>;
              if (docMap.containsKey('content_b64')) {
                _originalDocumentBase64 = docMap['content_b64'] as String?;
              }
            } catch (e) {
              print('Erreur lors de l\'extraction du contenu du document: $e');
            }
          }
        }
      }
      
      // Mettre à jour l'interface pour afficher les informations du document
      setState(() {
        _isVerifying = false;
        _isVerified = isValid;
        _documentTitle = documentTitle;
        
        if (!isValid) {
          // Gérer de façon sécurisée l'extraction du message d'erreur
          if (widget.verificationResult.containsKey('message')) {
            final message = widget.verificationResult['message'];
            if (message is String) {
              _errorMessage = message;
            } else {
              // Si le message n'est pas une chaîne, essayer de le convertir
              _errorMessage = message.toString();
            }
          } else {
            _errorMessage = 'La signature ne correspond pas au document original.';
          }
        }
      });
      
      // Créer une copie simplifiée des données pour l'historique (sans références circulaires)
      final Map<String, dynamic> simplifiedResult = {
        'valid': isValid,
        'document_id': widget.documentId,
        'verification_date': DateTime.now().toIso8601String(),
      };
      
      if (_signatureDate != null) {
        simplifiedResult['signature_date'] = _signatureDate!.toIso8601String();
      }
      
      if (documentTitle != 'Document non identifié') {
        simplifiedResult['document_title'] = documentTitle;
      }
      
      // Ajouter cette vérification à l'historique avec des données simplifiées
      final historyEntry = VerificationHistoryEntry(
        timestamp: DateTime.now(),
        signatureDate: _signatureDate,
        isVerified: isValid,
        qrData: {
          'document_id': widget.documentId,
          'verification_result': simplifiedResult,
        },
      );
      
      // Ajouter à l'historique
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
  
  /// Extrait les informations du signataire à partir des résultats de vérification
  Map<String, dynamic>? _extractSignerInfo() {
    try {
      // Cas 1: Les informations du signataire sont dans le nœud principal
      if (widget.verificationResult.containsKey('signer_info')) {
        final signerInfo = widget.verificationResult['signer_info'];
        if (signerInfo is Map<String, dynamic>) {
          return signerInfo;
        }
      }
      
      // Cas 2: Les informations du signataire sont dans api_response
      if (widget.verificationResult.containsKey('api_response') && 
          widget.verificationResult['api_response'] is Map<String, dynamic>) {
        final apiResponse = widget.verificationResult['api_response'] as Map<String, dynamic>;
        
        if (apiResponse.containsKey('signer_info')) {
          final signerInfo = apiResponse['signer_info'];
          if (signerInfo is Map<String, dynamic>) {
            return signerInfo;
          }
        }
      }
      
      // Cas 3: Les informations du signataire sont dans verification_info
      if (widget.verificationResult.containsKey('verification_info') && 
          widget.verificationResult['verification_info'] is Map<String, dynamic>) {
        final verificationInfo = widget.verificationResult['verification_info'] as Map<String, dynamic>;
        
        if (verificationInfo.containsKey('signer_info')) {
          final signerInfo = verificationInfo['signer_info'];
          if (signerInfo is Map<String, dynamic>) {
            return signerInfo;
          }
        }
      }
      
      // Aucune information de signataire trouvée
      return null;
    } catch (e) {
      print('Erreur lors de l\'extraction des informations du signataire: $e');
      return null;
    }
  }
  
  // La méthode _buildSignerInfoSection a été supprimée car les informations du signataire
  // sont maintenant affichées directement dans la liste principale des détails

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).colorScheme.primary;
    
    return Scaffold(
      body: Column(
        children: [
          // En-tête sombre uniforme avec bouton retour
          AppHeader(
            title: 'VÉRIFICATION',
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
  
  // Méthode _buildVerificationHeader supprimée car non utilisée
  
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
                'ANALYSE CRYPTOGRAPHIQUE',
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
                'Vérification de l\'authenticité de la signature et validation cryptographique des données. Cette opération ne prendra que quelques instants...',
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
            
            // Document Preview (si disponible)
            if (_originalDocumentBase64 != null) ...[              
              const SizedBox(height: 32),
              
              // Titre de la section aperçu du document signé
              Animate(
                effects: [
                  FadeEffect(
                    duration: const Duration(milliseconds: 400),
                    delay: const Duration(milliseconds: 150),
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
                        'DOCUMENT SIGNÉ AUTHENTIQUE',
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
                    delay: const Duration(milliseconds: 250),
                  ),
                ],
                child: _buildDocumentPreview(isDarkMode),
              ),
            ],
            
            const SizedBox(height: 32),
            
            // Détails de la signature
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
                    Icon(FontAwesomeIcons.fileCircleCheck, 
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
            
            // Liste des détails (simplifiée pour le nouveau format d'API)
            
            // Date de signature
            _buildDetailItem(
              isDarkMode: isDarkMode,
              icon: FontAwesomeIcons.calendarDays,
              title: 'Date de signature',
              value: _signatureDate != null
                  ? DateFormat('dd/MM/yyyy à HH:mm').format(_signatureDate!)
                  : widget.verificationResult.containsKey('api_response') && 
                    widget.verificationResult['api_response'].containsKey('signature_date')
                      ? widget.verificationResult['api_response']['signature_date']
                      : 'Non spécifiée',
              delay: 200,
            ),
            
            // 🆕 Type de signature
            if (_signatureType != null)
              _buildDetailItem(
                isDarkMode: isDarkMode,
                icon: _signatureType == 'ephemeral' ? FontAwesomeIcons.clock : FontAwesomeIcons.shieldHalved,
                title: 'Type de signature',
                value: _signatureType == 'ephemeral' ? 'Éphémère' : 'Pérenne',
                delay: 225,
              ),
            
            // 🆕 Date d'expiration (si signature éphémère)
            if (_signatureType == 'ephemeral' && _expirationDate != null)
              _buildDetailItem(
                isDarkMode: isDarkMode,
                icon: FontAwesomeIcons.calendarXmark,
                title: 'Date d\'expiration',
                value: DateFormat('dd/MM/yyyy à HH:mm').format(_expirationDate!),
                delay: 250,
              ),
            
            // ID du document
            _buildDetailItem(
              isDarkMode: isDarkMode,
              icon: FontAwesomeIcons.idCard,
              title: 'ID du document',
              value: _getPreviewText(widget.documentId),
              isLongValue: true,
              fullValue: widget.documentId,
              delay: _signatureType == 'ephemeral' ? 275 : 250,
            ),
            
            // Nom du document
            _buildDetailItem(
              isDarkMode: isDarkMode,
              icon: FontAwesomeIcons.fileLines,
              title: 'Nom du document',
              value: widget.verificationResult.containsKey('api_response') && 
                     widget.verificationResult['api_response'] is Map<String, dynamic> &&
                     (widget.verificationResult['api_response'] as Map<String, dynamic>).containsKey('original_filename')
                     ? widget.verificationResult['api_response']['original_filename']
                     : _documentTitle,
              delay: _signatureType == 'ephemeral' ? 325 : 300,
            ),
            
            // Titre de la section signataire
            const SizedBox(height: 24),
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
                    Icon(FontAwesomeIcons.userShield, 
                         color: colorScheme.primary, 
                         size: 20),
                    const SizedBox(width: 10),
                    Text(
                      'INFORMATION DU SIGNATAIRE',
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
            
            // Ajout direct des informations du signataire
            // Récupération des informations du signataire
            Builder(builder: (context) {
              final signerInfo = _extractSignerInfo();
              
              if (signerInfo == null) {
                return const SizedBox.shrink();
              }
              
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Nom complet du signataire
                  _buildDetailItem(
                    isDarkMode: isDarkMode,
                    icon: FontAwesomeIcons.user,
                    title: 'Nom du signataire',
                    value: signerInfo['full_name']?.toString() ?? 'Non spécifié',
                    delay: 350,
                  ),
                  
                  // Email du signataire
                  _buildDetailItem(
                    isDarkMode: isDarkMode,
                    icon: FontAwesomeIcons.envelope,
                    title: 'Email',
                    value: signerInfo['email']?.toString() ?? 'Non spécifié',
                    delay: 400,
                  ),
                  
                  // Organisation du signataire (si disponible)
                  if (signerInfo.containsKey('organization') && 
                      signerInfo['organization'] != null &&
                      signerInfo['organization'].toString().isNotEmpty)
                    _buildDetailItem(
                      isDarkMode: isDarkMode,
                      icon: FontAwesomeIcons.building,
                      title: 'Organisation',
                      value: signerInfo['organization'].toString(),
                      delay: 450,
                    ),
                  
                  // Rôle ou fonction du signataire
                  _buildDetailItem(
                    isDarkMode: isDarkMode,
                    icon: FontAwesomeIcons.idBadge,
                    title: 'Rôle',
                    value: signerInfo['role']?.toString() ?? 'Non spécifié',
                    delay: 500,
                  ),
                  
                  // Date de signature (si disponible)
                  if (_signatureDate != null)
                    _buildDetailItem(
                      isDarkMode: isDarkMode,
                      icon: FontAwesomeIcons.calendar,
                      title: 'Date de signature',
                      value: DateFormat('dd/MM/yyyy à HH:mm').format(_signatureDate!),
                      delay: 550,
                    ),
                ],
              );
            }),
            
            const SizedBox(height: 32),
            
            // Boutons d'action
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
                  ? (_isExpired ? FontAwesomeIcons.clock : FontAwesomeIcons.circleCheck)
                  : FontAwesomeIcons.circleXmark,
              size: 40,
              color: _isVerified 
                  ? (_isExpired ? Colors.orange : successColor)
                  : errorColor,
            ),
          ).animate(onPlay: (controller) => controller.repeat(reverse: true, period: const Duration(seconds: 3)))
            .scale(begin: const Offset(1.0, 1.0), end: const Offset(1.05, 1.05)),
          
          const SizedBox(height: 28),
          
          // Titre du résultat avec effet d'éclat
          Text(
            _isVerified 
                ? (_isExpired ? 'DOCUMENT AUTHENTIQUE MAIS EXPIRÉ' : 'DOCUMENT AUTHENTIQUE')
                : 'VÉRIFICATION ÉCHOUÉE',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.2,
                  color: _isVerified 
                      ? (_isExpired ? Colors.orange : successColor)
                      : errorColor,
                ),
          ),
          
          const SizedBox(height: 16),
          
          // Titre du document si disponible avec style amélioré
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
          
          // Message du résultat avec style amélioré
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            child: Text(
              _isVerified
                  ? (_isExpired 
                      ? 'Ce document est authentique mais sa signature a expiré. Il n\'est plus considéré comme valide.'
                      : 'La signature numérique de ce document a été vérifiée avec succès et authentifiée.')
                  : _errorMessage ?? 'La vérification du document a échoué. La signature pourrait être falsifiée.',
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
  
  // Méthode pour afficher la valeur complète dans une boîte de dialogue
  void _showFullValue(String title, String value) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SelectableText(
                value,
                style: const TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  OutlinedButton.icon(
                    icon: const Icon(Icons.copy),
                    label: const Text('Copier'),
                    onPressed: () {
                      Clipboard.setData(ClipboardData(text: value));
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('Copié dans le presse-papier'),
                          behavior: SnackBarBehavior.floating,
                        ),
                      );
                    },
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    child: const Text('Fermer'),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailItem({
    required bool isDarkMode,
    required IconData icon,
    required String title,
    required String value,
    bool isLongValue = false,
    String? fullValue,
    required int delay,
  }) {
    // Couleur de fond de la carte de détail avec un contraste légèrement plus élevé
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
          color: cardBgColor, // Utilisation de la variable cardBgColor pour les items
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
              child: isLongValue && fullValue != null
                  ? Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          value,
                          style: TextStyle(
                            color: isDarkMode
                                ? Colors.grey[300]
                                : Colors.grey[700],
                            fontFamily: 'monospace',
                            fontSize: 14,
                            letterSpacing: 0.3,
                          ),
                        ),
                        const SizedBox(height: 12),
                        InkWell(
                          onTap: () => _showFullValue(title, fullValue),
                          borderRadius: BorderRadius.circular(8),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            decoration: BoxDecoration(
                              color: primaryColor.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  'Voir plus',
                                  style: TextStyle(
                                    color: primaryColor,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                  ),
                                ),
                                const SizedBox(width: 6),
                                Icon(
                                  FontAwesomeIcons.angleRight,
                                  size: 14,
                                  color: primaryColor,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    )
                  : Text(
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
  
  /// Crée un aperçu sécurisé du texte en vérifiant la longueur
  String _getPreviewText(String text, {int previewLength = 15}) {
    if (text.length <= previewLength) return text;
    return '${text.substring(0, previewLength)}...';
  }
  
  /// Construit un aperçu du document signé à partir des données base64
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
                'Document signé certifié',
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
          height: 320, // Taille augmentée pour une meilleure prévisualisation
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
                // Si un aperçu du document signé est disponible, l'afficher avec notre utilitaire
                if (_originalDocumentBase64 != null)
                  DocumentPreviewUtils.renderDocumentPreview(
                    context, 
                    _originalDocumentBase64!, 
                    _documentTitle,
                    _isVerified,
                  ),
                
                // Superposition d'un effet de papier d'authentification
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
                
                // Bouton pour télécharger le document signé
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
                              content: Text('Document signé non disponible'),
                              duration: Duration(seconds: 2),
                              backgroundColor: Colors.orange,
                            ),
                          );
                        }
                      },
                    ),
                  ),
                ),
                
                // Bouton pour voir le document signé en plein écran
                Positioned(
                  bottom: 16,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: TextButton.icon(
                      onPressed: () => _showFullDocumentPreview(),
                      icon: const Icon(FontAwesomeIcons.fileShield, size: 18),
                      label: const Text('Voir le document signé'),
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

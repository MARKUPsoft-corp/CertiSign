import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../../core/theme.dart';
import '../../services/signature_service.dart';
import '../../shared/app_header.dart';
import '../verify/verify_screen.dart';
import '../verify/verify_screen_legacy.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> with SingleTickerProviderStateMixin {
  // Contrôleur pour le scanner
  late MobileScannerController _scannerController;
  bool _isFlashOn = false;
  bool _isFrontCamera = false;
  bool _isScanning = true;
  bool _scannerInitialized = false;
  
  // Service de vérification de signature
  final SignatureService _signatureService = SignatureService();
  
  // Effet d'overlay pour le scanner
  late AnimationController _animationController;
  late Animation<double> _animation;
  
  @override
  void initState() {
    super.initState();
    
    // Configuration de l'animation pour l'overlay scanner
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );
    
    _animation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.linear,
      ),
    );
    
    _animationController.repeat(reverse: true);
    
    // Initialisation optimisée du scanner
    _initializeScanner();
  }
  
  Future<void> _initializeScanner() async {
    // Configuration ultra-rapide pour les QR codes
    _scannerController = MobileScannerController(
      // Détecter uniquement les QR codes
      formats: const [BarcodeFormat.qrCode],
      // Détection la plus rapide possible
      detectionSpeed: DetectionSpeed.normal,
      // Mode performance optimisée pour la vitesse
      detectionTimeoutMs: 500, // Réduire le délai de détection
      facing: CameraFacing.back,
      autoStart: true,
      torchEnabled: _isFlashOn,
      // Résolution standard pour équilibrer vitesse et précision
      cameraResolution: const Size(720, 1280),
    );
    
    // Attendre un court instant pour garantir l'initialisation complète
    await Future.delayed(const Duration(milliseconds: 100));
    
    if (mounted) {
      setState(() {
        _scannerInitialized = true;
      });
    }
  }
  
  @override
  void dispose() {
    _scannerController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    
    return Scaffold(
      body: Stack(
        children: [
          // Scanner QR optimisé pour la vitesse
          SizedBox.expand(
            child: _scannerInitialized
            ? MobileScanner(
                controller: _scannerController,
                onDetect: _onDetect,
                // Plein écran pour une détection plus rapide
                // L'overlay visuel guidera l'utilisateur
              )
            : Center(
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Theme.of(context).primaryColor),
                ),
              ),
          ),
          
          // Overlay scanner
          Positioned.fill(
            child: AnimatedBuilder(
              animation: _animationController,
              builder: (context, child) {
                return _buildScannerOverlay(isDarkMode);
              },
            ),
          ),
          
          // Interface supérieure
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: EdgeInsets.only(
                top: MediaQuery.of(context).padding.top + 16,
                bottom: 16,
                left: 16,
                right: 16,
              ),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withOpacity(0.7),
                    Colors.transparent,
                  ],
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Bouton de retour
                  IconButton(
                    icon: const Icon(
                      Icons.arrow_back_ios_rounded,
                      color: Colors.white,
                    ),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                  
                  // Titre
                  const Text(
                    'Scanner un QR Code',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  
                  // Espace équivalent au bouton de retour
                  const SizedBox(width: 48),
                ],
              ),
            ),
          ),
          
          // Contrôles inférieurs
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).padding.bottom + 16,
                top: 16,
                left: 16,
                right: 16,
              ),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.bottomCenter,
                  end: Alignment.topCenter,
                  colors: [
                    Colors.black.withOpacity(0.7),
                    Colors.transparent,
                  ],
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // Contrôle du flash
                  IconButton(
                    icon: Icon(
                      _isFlashOn ? Icons.flash_on : Icons.flash_off,
                      color: Colors.white,
                      size: 28,
                    ),
                    onPressed: () {
                      setState(() {
                        _isFlashOn = !_isFlashOn;
                        _scannerController.toggleTorch();
                      });
                    },
                  ),
                  
                  // Instructions de scan
                  const Text(
                    'Positionnez le QR Code dans le cadre',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                    ),
                  ),
                  
                  // Changement de caméra
                  IconButton(
                    icon: Icon(
                      _isFrontCamera ? Icons.camera_rear : Icons.camera_front,
                      color: Colors.white,
                      size: 28,
                    ),
                    onPressed: () {
                      setState(() {
                        _isFrontCamera = !_isFrontCamera;
                        _scannerController.switchCamera();
                      });
                    },
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildScannerOverlay(bool isDarkMode) {
    final scanAreaSize = MediaQuery.of(context).size.width * 0.7;
    final scanAreaPosY = (MediaQuery.of(context).size.height - scanAreaSize) / 2;
    
    return CustomPaint(
      size: Size.infinite,
      painter: ScannerOverlayPainter(
        scanAreaSize: scanAreaSize,
        scanAreaPosY: scanAreaPosY,
        scanLinePosition: _animation.value,
        primaryColor: isDarkMode 
            ? AppTheme.darkPrimaryColor 
            : AppTheme.primaryColor,
      ),
    );
  }
  
  void _onDetect(BarcodeCapture capture) async {
    if (!_isScanning) return;
    
    final List<Barcode> barcodes = capture.barcodes;
    if (barcodes.isEmpty) return;
    
    // Traitement instantané sans setState préliminaire pour optimiser la vitesse
    _isScanning = false;
    _scannerController.stop();
    
    // Vibration pour indiquer la détection
    HapticFeedback.lightImpact();
    
    final barcode = barcodes.first;
    final String? qrContent = barcode.rawValue;
    
    if (qrContent == null || qrContent.isEmpty) {
      _showErrorSnackbar('QR Code vide ou invalide');
      _returnToHome();
      return;
    }
    
    print('QR Code détecté: $qrContent');
    
    // Traitement de vérification
    Future.microtask(() async {
      if (!mounted) return;
      
      try {
        // Afficher l'indicateur de vérification
        _showVerifyingDialog();
        
        // 1. Extraire l'ID du document depuis le QR code
        final documentId = _signatureService.extractDocumentId(qrContent);
        if (documentId == null) {
          // Fermer l'indicateur de vérification
          if (mounted) Navigator.of(context).pop();
          _showErrorSnackbar('QR Code invalide: aucun ID de document trouvé');
          _returnToHome();
          return;
        }
        
        print('ID du document extrait: $documentId');
        
        // 2. Vérifier le type de document et utiliser la bonne API
        Map<String, dynamic> verificationResult;
        String cleanDocumentId;
        bool isAndroidFormat = false;
        
        if (documentId.startsWith('android:')) {
          // Format androidSignature - utiliser l'API docs.camgovca.cm
          isAndroidFormat = true;
          final androidSignature = documentId.substring(8); // Retirer le préfixe 'android:'
          cleanDocumentId = androidSignature.substring(344); // Extraire l'ID propre
          
          print('🔄 Format androidSignature détecté - utilisation de l\'API docs.camgovca.cm');
          verificationResult = await _signatureService.verifyDocumentWithDocsAPI(androidSignature);
        } else {
          // Format UUID classique - utiliser l'API existante
          cleanDocumentId = documentId;
          print('🔄 Format UUID détecté - utilisation de l\'API standard');
          verificationResult = await _signatureService.verifyDocumentWithServer(documentId);
        }
        
        // Fermer l'indicateur de vérification
        if (mounted) Navigator.of(context).pop();
        
        // 3. Navigation vers l'écran approprié selon le format
        if (mounted) {
          if (isAndroidFormat) {
            // Router vers la page legacy pour les documents androidSignature
            print('Navigation vers l\'écran de vérification legacy');
            
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (context) => VerifyScreenLegacy(
                  documentId: cleanDocumentId,
                  verificationResult: verificationResult,
                ),
              ),
            ).then((_) => _resetScanner());
          } else {
            // Router vers la page normale pour les UUID
            print('Navigation vers l\'écran de vérification standard');
            
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (context) => VerifyScreen(
                  documentId: cleanDocumentId,
                  verificationResult: verificationResult,
                ),
              ),
            ).then((_) => _resetScanner());
          }
        }
      } catch (e, stackTrace) {
        // En cas d'erreur inattendue, fermer le dialogue et afficher un message
        print('ERREUR CRITIQUE: $e');
        print('Stack trace: $stackTrace');
        
        if (mounted) {
          Navigator.of(context).pop(); // Fermer dialogue de vérification
          _showErrorSnackbar('Erreur lors de la vérification: ${e.toString().substring(0, min(100, e.toString().length))}');
          _returnToHome();
        }
      }
    });
  }
  
  // Méthode pour retourner à la page d'accueil après une erreur
  void _returnToHome() {
    Future.delayed(const Duration(milliseconds: 1500), () {
      if (mounted) {
        try {
          Navigator.of(context).pop(); // Retour à l'accueil
        } catch (e) {
          print('Erreur lors du retour à l\'accueil: $e');
        }
      }
      _resetScanner(); // Réinitialisation du scanner pour une utilisation future
    });
  }
  
  // Fonction d'utilitaire pour éviter les dépassements
  int min(int a, int b) {
    return (a < b) ? a : b;
  }
  
  // Dialogue pour afficher que la vérification est en cours
  void _showVerifyingDialog() {
    if (!mounted) return;
    
    showDialog(
      context: context,
      barrierDismissible: false, // L'utilisateur ne peut pas fermer cette fenêtre
      builder: (BuildContext context) {
        return AlertDialog(
          content: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Theme.of(context).primaryColor),
              ),
              const SizedBox(width: 24),
              const Text(
                'Vérification...',
                style: TextStyle(fontSize: 16),
              ),
            ],
          ),
        );
      },
    );
  }
  
  // Affiche une belle boîte d'erreur stylisée centrée
  void _showErrorSnackbar(String message) {
    // Arrêt temporaire du scanner pour permettre à l'utilisateur de lire le message d'erreur
    _scannerController.stop();
    
    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (BuildContext context) {
        return Dialog(
          backgroundColor: Colors.transparent,
          elevation: 0,
          child: Container(
            width: double.infinity,
            constraints: const BoxConstraints(maxWidth: 350),
            padding: const EdgeInsets.all(0),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // En-tête avec icône et fond dégradé
                Container(
                  padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 24),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        const Color(0xFFEF4444),
                        const Color(0xFFDC2626),
                      ],
                    ),
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(24),
                      topRight: Radius.circular(24),
                    ),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: const Icon(
                          Icons.qr_code_scanner,
                          color: Colors.white,
                          size: 28,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'QR CODE INVALIDE',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                letterSpacing: 1,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Une erreur a été détectée',
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.9),
                                fontSize: 14,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Corps du message d'erreur
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.only(
                      bottomLeft: Radius.circular(24),
                      bottomRight: Radius.circular(24),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        message,
                        style: const TextStyle(
                          fontSize: 15,
                          color: Color(0xFF334155),
                          height: 1.4,
                        ),
                      ),
                      const SizedBox(height: 24),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          TextButton(
                            onPressed: () {
                              Navigator.of(context).pop();
                              _resetScanner();
                            },
                            style: TextButton.styleFrom(
                              foregroundColor: const Color(0xFFDC2626),
                            ),
                            child: const Text('ANNULER'),
                          ),
                          const SizedBox(width: 8),
                          ElevatedButton(
                            onPressed: () {
                              Navigator.of(context).pop();
                              _resetScanner();
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFFDC2626),
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            child: const Text('RÉESSAYER'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
  
  void _resetScanner() {
    // Redémarrage immédiat pour une expérience plus réactive
    Future.microtask(() {
      if (!mounted) return;
      
      _scannerController.start();
      _isScanning = true;
      
      // Mettre à jour l'interface seulement après le démarrage de la caméra
      setState(() {});
    });
  }
}

class ScannerOverlayPainter extends CustomPainter {
  final double scanAreaSize;
  final double scanAreaPosY;
  final double scanLinePosition;
  final Color primaryColor;
  
  ScannerOverlayPainter({
    required this.scanAreaSize,
    required this.scanAreaPosY,
    required this.scanLinePosition,
    required this.primaryColor,
  });
  
  @override
  void paint(Canvas canvas, Size size) {
    final scanAreaRect = Rect.fromLTWH(
      (size.width - scanAreaSize) / 2,
      scanAreaPosY,
      scanAreaSize,
      scanAreaSize,
    );
    
    // Nouvelle approche pour le rendu de la zone de scan
    // Créer un chemin pour tout l'écran sauf la zone de scan
    final path = Path()
      ..addRect(Rect.fromLTWH(0, 0, size.width, size.height))
      ..addRect(scanAreaRect)
      ..fillType = PathFillType.evenOdd;
    
    // Dessiner le fond semi-transparent uniquement dans les zones extérieures au cadre de scan
    final backgroundPaint = Paint()
      ..color = Colors.black.withOpacity(0.5)
      ..style = PaintingStyle.fill;
    
    canvas.drawPath(path, backgroundPaint);
    
    // Dessiner les coins du cadre de scan
    final cornerSize = scanAreaSize * 0.1;
    final cornerPaint = Paint()
      ..color = primaryColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;
    
    // Coin supérieur gauche
    canvas.drawPath(
      Path()
        ..moveTo(scanAreaRect.left, scanAreaRect.top + cornerSize)
        ..lineTo(scanAreaRect.left, scanAreaRect.top)
        ..lineTo(scanAreaRect.left + cornerSize, scanAreaRect.top),
      cornerPaint,
    );
    
    // Coin supérieur droit
    canvas.drawPath(
      Path()
        ..moveTo(scanAreaRect.right - cornerSize, scanAreaRect.top)
        ..lineTo(scanAreaRect.right, scanAreaRect.top)
        ..lineTo(scanAreaRect.right, scanAreaRect.top + cornerSize),
      cornerPaint,
    );
    
    // Coin inférieur gauche
    canvas.drawPath(
      Path()
        ..moveTo(scanAreaRect.left, scanAreaRect.bottom - cornerSize)
        ..lineTo(scanAreaRect.left, scanAreaRect.bottom)
        ..lineTo(scanAreaRect.left + cornerSize, scanAreaRect.bottom),
      cornerPaint,
    );
    
    // Coin inférieur droit
    canvas.drawPath(
      Path()
        ..moveTo(scanAreaRect.right - cornerSize, scanAreaRect.bottom)
        ..lineTo(scanAreaRect.right, scanAreaRect.bottom)
        ..lineTo(scanAreaRect.right, scanAreaRect.bottom - cornerSize),
      cornerPaint,
    );
    
    // Ligne de scan animée
    final scanLineY = scanAreaRect.top + (scanAreaRect.height * scanLinePosition);
    final scanLinePaint = Paint()
      ..color = primaryColor.withOpacity(0.8)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    
    canvas.drawLine(
      Offset(scanAreaRect.left, scanLineY),
      Offset(scanAreaRect.right, scanLineY),
      scanLinePaint,
    );
    
    // Effet de lueur sur la ligne de scan
    final glowPaint = Paint()
      ..color = primaryColor.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
    
    canvas.drawLine(
      Offset(scanAreaRect.left, scanLineY),
      Offset(scanAreaRect.right, scanLineY),
      glowPaint,
    );
  }
  
  @override
  bool shouldRepaint(ScannerOverlayPainter oldDelegate) =>
      oldDelegate.scanLinePosition != scanLinePosition;
}

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:path_provider/path_provider.dart';
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';

class DocumentPreviewUtils {
  /// Méthode pour rendre un aperçu de document à partir de données base64
  static Widget renderDocumentPreview(
    BuildContext context, 
    String base64Data, 
    String documentTitle,
    bool isVerified,
  ) {
    try {
      // Essayer de décoder les données base64
      final bytes = base64.decode(base64Data.replaceAll('\n', ''));
      
      // Vérifier si c'est un PDF (commence par %PDF)
      final isPdf = bytes.length > 4 && 
                    String.fromCharCodes(bytes.sublist(0, 4)) == '%PDF';
      
      if (isPdf) {
        // Pour les PDF, utiliser le visualiseur SyncFusion
        return SfPdfViewer.memory(
          bytes,
          canShowScrollHead: false,
          canShowScrollStatus: false,
          pageSpacing: 0,
          enableDoubleTapZooming: true,
        );
      } else {
        // Essayer d'afficher comme une image
        try {
          return Container(
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: Colors.grey.shade50,
            ),
            child: Image.memory(
              bytes,
              fit: BoxFit.contain,
              errorBuilder: (context, error, stackTrace) {
                // En cas d'erreur, afficher une icône générique de document
                return Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        FontAwesomeIcons.fileLines,
                        size: 64,
                        color: Colors.blueGrey,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        documentTitle,
                        style: Theme.of(context).textTheme.titleMedium,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Format non visualisable',
                        style: Theme.of(context).textTheme.bodyMedium,
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                );
              },
            ),
          );
        } catch (e) {
          // Fallback pour tout autre type de document
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  FontAwesomeIcons.fileLines,
                  size: 64,
                  color: Colors.blueGrey,
                ),
                const SizedBox(height: 16),
                Text(
                  documentTitle,
                  style: Theme.of(context).textTheme.titleMedium,
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          );
        }
      }
    } catch (e) {
      print('Erreur de rendu du document: $e');
      return const Center(
        child: Text('Impossible d\'afficher le document'),
      );
    }
  }
  
  /// Méthode pour sauvegarder le document dans les téléchargements
  static Future<void> saveDocument(BuildContext context, String base64Data, String documentTitle) async {
    try {
      final bytes = base64.decode(base64Data.replaceAll('\n', ''));
      
      // Déterminer l'extension de fichier
      String extension = '.pdf';
      if (bytes.length > 4) {
        final header = String.fromCharCodes(bytes.sublist(0, 4));
        if (header == '%PDF') {
          extension = '.pdf';
        } else if (bytes.length > 10 && 
                  (bytes[0] == 0xFF && bytes[1] == 0xD8 && bytes[2] == 0xFF)) {
          extension = '.jpg';
        } else if (bytes.length > 8 && 
                  (bytes[0] == 0x89 && bytes[1] == 0x50 && bytes[2] == 0x4E && bytes[3] == 0x47)) {
          extension = '.png';
        }
      }
      
      // Créer un nom de fichier sécurisé
      final sanitizedName = documentTitle
          .replaceAll(RegExp(r'[^\w\s.-]'), '')
          .replaceAll(RegExp(r'\s+'), '_');
      final fileName = sanitizedName.isEmpty ? 'document$extension' : '$sanitizedName$extension';

      // Obtenir le répertoire de téléchargement
      final directory = await getApplicationDocumentsDirectory();
      final filePath = '${directory.path}/$fileName';
      
      // Écrire les données dans un fichier
      final file = File(filePath);
      await file.writeAsBytes(bytes);
      
      // Copier le contenu dans le presse-papier si c'est un texte
      if (extension != '.pdf' && extension != '.jpg' && extension != '.png') {
        try {
          final text = utf8.decode(bytes);
          await Clipboard.setData(ClipboardData(text: text));
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Contenu copié dans le presse-papier'),
              duration: Duration(seconds: 2),
            ),
          );
        } catch (e) {
          // Ignorer l'erreur si ce n'est pas du texte
        }
      }
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Document enregistré dans: $filePath'),
          duration: const Duration(seconds: 3),
          action: SnackBarAction(
            label: 'OK',
            onPressed: () {},
          ),
        ),
      );
      
    } catch (e) {
      print('Erreur lors de la sauvegarde: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erreur: $e'),
          duration: const Duration(seconds: 2),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  /// Méthode pour afficher un document en plein écran
  static void showFullDocumentPreview(
    BuildContext context, 
    String base64Data, 
    String documentTitle,
    bool isVerified,
  ) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        insetPadding: const EdgeInsets.all(16),
        child: Container(
          width: double.infinity,
          height: double.infinity,
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // Barre de titre avec bouton de fermeture
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      documentTitle,
                      style: Theme.of(context).textTheme.titleLarge,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(FontAwesomeIcons.xmark),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const Divider(),
              // Zone d'affichage du document
              Expanded(
                child: Container(
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Stack(
                    children: [
                      renderDocumentPreview(context, base64Data, documentTitle, isVerified),
                      // Filigrane de vérification
                      if (isVerified)
                        Positioned.fill(
                          child: IgnorePointer(
                            child: Center(
                              child: Opacity(
                                opacity: 0.12,
                                child: Transform.rotate(
                                  angle: -0.3,
                                  child: Text(
                                    'CertiSign, Authentique',
                                    style: TextStyle(
                                      fontSize: 36,
                                      fontWeight: FontWeight.bold,
                                      color: Theme.of(context).colorScheme.primary,
                                    ),
                                  ),
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
          ),
        ),
      ),
    );
  }
}

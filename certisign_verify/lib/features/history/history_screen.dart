import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:intl/intl.dart';

import '../../core/theme.dart';
import 'verification_history.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<VerificationHistoryEntry> _historyEntries = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() {
      _isLoading = true;
    });

    // Attendre un court délai pour l'animation
    await Future.delayed(const Duration(milliseconds: 300));
    
    // Charger l'historique
    final history = await VerificationHistory.instance.getHistory();
    
    setState(() {
      _historyEntries = history;
      _isLoading = false;
    });
  }

  Future<void> _clearHistory() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Effacer l\'historique'),
        content: const Text(
          'Êtes-vous sûr de vouloir effacer tout l\'historique des vérifications ?'
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Annuler'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.dangerColor,
            ),
            child: const Text('Effacer'),
          ),
        ],
      ),
    ) ?? false;

    if (confirmed) {
      await VerificationHistory.instance.clearHistory();
      _loadHistory();
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Historique effacé'),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).colorScheme.primary;
    
    return Scaffold(
      appBar: AppBar(
        centerTitle: true,
        elevation: 0,
        backgroundColor: Colors.transparent,
        title: Text(
          'HISTORIQUE',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            letterSpacing: 2,
            color: primaryColor,
          ),
        ),
        actions: [
          if (_historyEntries.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: IconButton(
                icon: Icon(
                  Icons.delete_outline,
                  color: AppTheme.dangerColor.withOpacity(0.8),
                ),
                onPressed: _clearHistory,
                tooltip: 'Effacer l\'historique',
              ),
            ),
        ],
      ),
      body: Stack(
        children: [
          // Cercles de décoration
          Positioned(
            top: -50,
            right: -50,
            child: Container(
              width: 150,
              height: 150,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isDarkMode 
                    ? AppTheme.darkPrimaryColor.withOpacity(0.1) 
                    : AppTheme.primaryColor.withOpacity(0.1),
              ),
            ),
          ),
          
          Positioned(
            bottom: -80,
            left: -60,
            child: Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isDarkMode 
                    ? AppTheme.darkAccentColor.withOpacity(0.1) 
                    : AppTheme.accentColor.withOpacity(0.1),
              ),
            ),
          ),
          
          // Contenu principal
          SafeArea(
            child: _isLoading
                ? _buildLoadingState()
                : _historyEntries.isEmpty
                    ? _buildEmptyState(context)
                    : _buildHistoryList(context),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).colorScheme.primary;
    
    return Center(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 32),
        padding: const EdgeInsets.all(30),
        decoration: BoxDecoration(
          color: isDarkMode 
              ? Colors.black.withOpacity(0.2) 
              : Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(isDarkMode ? 0.2 : 0.05),
              blurRadius: 20,
              offset: const Offset(0, 10),
              spreadRadius: 0,
            ),
          ],
          border: Border.all(
            color: primaryColor.withOpacity(0.1),
            width: 1.5,
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Icône décorative pour l'historique
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: primaryColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                FontAwesomeIcons.clockRotateLeft,
                size: 36,
                color: primaryColor,
              ),
            )
            .animate()
            .fadeIn(duration: 600.ms)
            .scale(begin: const Offset(0.5, 0.5), end: const Offset(1, 1)),
            
            const SizedBox(height: 24),
            
            // Titre
            Text(
              'Aucun historique',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: primaryColor,
                  ),
            )
            .animate()
            .fadeIn(duration: 500.ms, delay: 200.ms),
            
            const SizedBox(height: 16),
            
            // Message descriptif
            Text(
              'Les vérifications de signatures électroniques que vous effectuerez seront enregistrées et affichées ici pour référence future.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).textTheme.bodySmall?.color,
                    height: 1.5,
                  ),
              textAlign: TextAlign.center,
            )
            .animate()
            .fadeIn(duration: 500.ms, delay: 300.ms),
            
            const SizedBox(height: 24),
            
            // Bouton de scan
            ElevatedButton.icon(
              onPressed: () {
                Navigator.of(context).pop(); // Retour à l'écran d'accueil
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: primaryColor,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 2,
              ),
              icon: const Icon(FontAwesomeIcons.qrcode, size: 18),
              label: const Text('Scanner un QR Code'),
            )
            .animate()
            .fadeIn(duration: 500.ms, delay: 400.ms)
            .slideY(begin: 0.2, end: 0),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryList(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      itemCount: _historyEntries.length,
      itemBuilder: (context, index) {
        final entry = _historyEntries[index];
        return _buildHistoryItem(context, entry, index);
      },
    );
  }

  Widget _buildHistoryItem(
    BuildContext context, 
    VerificationHistoryEntry entry,
    int index,
  ) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).colorScheme.primary;
    
    final statusColor = entry.isVerified
        ? AppTheme.successColor
        : AppTheme.dangerColor;
    
    final formattedDate = DateFormat('dd/MM/yyyy HH:mm').format(entry.timestamp);
    final signatureDate = entry.signatureDate != null
        ? DateFormat('dd/MM/yyyy').format(entry.signatureDate!)
        : 'Non spécifiée';
    
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: isDarkMode 
            ? Colors.black.withOpacity(0.2) 
            : Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(isDarkMode ? 0.2 : 0.05),
            blurRadius: 15,
            offset: const Offset(0, 5),
            spreadRadius: 0,
          ),
        ],
        border: Border.all(
          color: entry.isVerified 
              ? statusColor.withOpacity(0.1) 
              : statusColor.withOpacity(0.1),
          width: 1.5,
        ),
      ),
      child: Column(
        children: [
          // En-tête de la carte avec le statut
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: statusColor.withOpacity(0.1),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(15),
                topRight: Radius.circular(15),
              ),
            ),
            child: Row(
              children: [
                // Icône de statut
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.2),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: statusColor.withOpacity(0.3),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Center(
                    child: Icon(
                      entry.isVerified
                          ? FontAwesomeIcons.check
                          : FontAwesomeIcons.xmark,
                      color: statusColor,
                      size: 14,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                
                // Titre avec le statut
                Expanded(
                  child: Text(
                    entry.isVerified
                        ? 'Signature authentique'
                        : 'Signature non-valide',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: statusColor,
                    ),
                  ),
                ),
                
                // Bouton de détails
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: isDarkMode 
                        ? Colors.black.withOpacity(0.2) 
                        : Colors.white.withOpacity(0.8),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    Icons.arrow_forward_ios_rounded,
                    color: statusColor,
                    size: 16,
                  ),
                ),
              ],
            ),
          ),
          
          // Corps de la carte avec les dates
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Date de vérification
                Row(
                  children: [
                    Icon(
                      Icons.access_time_rounded,
                      size: 18,
                      color: primaryColor.withOpacity(0.7),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Vérifié le: ',
                        style: TextStyle(
                          fontWeight: FontWeight.w500,
                          color: primaryColor.withOpacity(0.7),
                        ),
                      ),
                    ),
                    Text(
                      formattedDate,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: isDarkMode ? Colors.white70 : Colors.black87,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 8),
                
                // Date de signature
                Row(
                  children: [
                    Icon(
                      FontAwesomeIcons.penNib,
                      size: 16,
                      color: primaryColor.withOpacity(0.7),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Date de signature: ',
                        style: TextStyle(
                          fontWeight: FontWeight.w500,
                          color: primaryColor.withOpacity(0.7),
                        ),
                      ),
                    ),
                    Text(
                      signatureDate,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: isDarkMode ? Colors.white70 : Colors.black87,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    )
    .animate()
    .fadeIn(duration: 500.ms, delay: (index * 50).ms)
    .slideY(begin: 0.1, end: 0);
  }
}

import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

/// Classe représentant une entrée dans l'historique des vérifications
class VerificationHistoryEntry {
  final DateTime timestamp;
  final DateTime? signatureDate;
  final bool isVerified;
  final Map<String, dynamic> qrData;

  VerificationHistoryEntry({
    required this.timestamp,
    this.signatureDate,
    required this.isVerified,
    required this.qrData,
  });

  /// Convertit l'entrée en Map pour le stockage
  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp.toIso8601String(),
      'signatureDate': signatureDate?.toIso8601String(),
      'isVerified': isVerified,
      'qrData': qrData,
    };
  }

  /// Crée une entrée à partir d'un Map
  factory VerificationHistoryEntry.fromJson(Map<String, dynamic> json) {
    return VerificationHistoryEntry(
      timestamp: DateTime.parse(json['timestamp']),
      signatureDate: json['signatureDate'] != null 
          ? DateTime.parse(json['signatureDate']) 
          : null,
      isVerified: json['isVerified'],
      qrData: json['qrData'],
    );
  }
}

/// Gestionnaire d'historique de vérification
class VerificationHistory {
  static const String _storageKey = 'verification_history';
  static final VerificationHistory _instance = VerificationHistory._internal();
  
  List<VerificationHistoryEntry> _history = [];
  bool _isInitialized = false;

  /// Instance singleton
  static VerificationHistory get instance => _instance;

  VerificationHistory._internal();

  /// Initialise l'historique depuis le stockage
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = prefs.getString(_storageKey);
      
      if (historyJson != null) {
        final List<dynamic> historyList = json.decode(historyJson);
        _history = historyList
            .map((item) => VerificationHistoryEntry.fromJson(item))
            .toList();
      }
      
      _isInitialized = true;
    } catch (e) {
      print('Erreur lors de l\'initialisation de l\'historique: $e');
      _history = [];
      _isInitialized = true;
    }
  }

  /// Ajoute une vérification à l'historique
  Future<void> addVerification(VerificationHistoryEntry entry) async {
    // S'assurer que l'historique est initialisé
    if (!_isInitialized) {
      await initialize();
    }
    
    // Ajouter l'entrée
    _history.insert(0, entry);
    
    // Limiter la taille de l'historique (garder les 50 dernières vérifications)
    if (_history.length > 50) {
      _history = _history.sublist(0, 50);
    }
    
    // Sauvegarder l'historique
    await _saveHistory();
  }

  /// Récupère l'historique complet
  Future<List<VerificationHistoryEntry>> getHistory() async {
    if (!_isInitialized) {
      await initialize();
    }
    
    return List.unmodifiable(_history);
  }

  /// Efface tout l'historique
  Future<void> clearHistory() async {
    _history.clear();
    await _saveHistory();
  }

  /// Sauvegarde l'historique dans le stockage local
  Future<void> _saveHistory() async {
    try {
      final historyJson = json.encode(
        _history.map((entry) => entry.toJson()).toList(),
      );
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_storageKey, historyJson);
    } catch (e) {
      print('Erreur lors de la sauvegarde de l\'historique: $e');
    }
  }
}

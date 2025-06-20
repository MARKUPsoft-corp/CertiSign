import 'dart:developer';

/// Utilitaire pour mesurer les performances de l'application
class PerformanceProfiler {
  static final Map<String, Stopwatch> _watches = {};
  static bool _enabled = true;

  /// Active ou désactive les logs de performance
  static void setEnabled(bool enabled) {
    _enabled = enabled;
  }

  /// Démarre la mesure pour une opération spécifique
  static void startMeasure(String operationName) {
    if (!_enabled) return;
    
    if (_watches.containsKey(operationName)) {
      _watches[operationName]!.reset();
    } else {
      _watches[operationName] = Stopwatch();
    }
    
    _watches[operationName]!.start();
  }

  /// Termine la mesure et renvoie la durée en millisecondes
  static int endMeasure(String operationName) {
    if (!_enabled || !_watches.containsKey(operationName)) return -1;
    
    final watch = _watches[operationName]!;
    watch.stop();
    
    final duration = watch.elapsedMilliseconds;
    
    log('Performance: $operationName took $duration ms');
    
    return duration;
  }

  /// Wrapper pour exécuter et mesurer une fonction
  static T measure<T>(String operationName, T Function() function) {
    startMeasure(operationName);
    final result = function();
    endMeasure(operationName);
    
    return result;
  }
}

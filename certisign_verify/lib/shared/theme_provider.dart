import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeProvider extends ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.system;
  bool _isDarkMode = false;

  ThemeProvider() {
    _loadTheme();
  }

  ThemeMode get themeMode => _themeMode;
  bool get isDarkMode => _isDarkMode;

  set themeMode(ThemeMode mode) {
    _themeMode = mode;
    _isDarkMode = mode == ThemeMode.dark;
    _saveTheme();
    notifyListeners();
  }

  void toggleTheme() {
    _isDarkMode = !_isDarkMode;
    _themeMode = _isDarkMode ? ThemeMode.dark : ThemeMode.light;
    _saveTheme();
    notifyListeners();
  }

  Future<void> _loadTheme() async {
    final prefs = await SharedPreferences.getInstance();
    final savedThemeMode = prefs.getString('themeMode');
    
    if (savedThemeMode == 'dark') {
      _themeMode = ThemeMode.dark;
      _isDarkMode = true;
    } else if (savedThemeMode == 'light') {
      _themeMode = ThemeMode.light;
      _isDarkMode = false;
    } else {
      // Par défaut, utiliser le mode sombre
      _isDarkMode = true;
      _themeMode = ThemeMode.dark;
    }
    
    notifyListeners();
  }

  Future<void> _saveTheme() async {
    final prefs = await SharedPreferences.getInstance();
    String themeStr = 'system';
    
    if (_themeMode == ThemeMode.dark) {
      themeStr = 'dark';
    } else if (_themeMode == ThemeMode.light) {
      themeStr = 'light';
    }
    
    await prefs.setString('themeMode', themeStr);
  }
}

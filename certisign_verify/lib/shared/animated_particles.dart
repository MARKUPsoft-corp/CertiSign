import 'dart:math';
import 'package:flutter/material.dart';
import '../core/theme.dart';

class AnimatedParticles extends StatefulWidget {
  final int particleCount;
  final double opacity;
  final double maxSize;
  
  const AnimatedParticles({
    super.key, 
    this.particleCount = 8,  // Réduit pour de meilleures performances
    this.opacity = 0.2,      // Moins visible, moins intensif
    this.maxSize = 4,        // Plus petit, meilleure performance
  });

  @override
  AnimatedParticlesState createState() => AnimatedParticlesState();
}

class AnimatedParticlesState extends State<AnimatedParticles> with TickerProviderStateMixin {
  final List<ParticleModel> _particles = [];
  late AnimationController _animationController;
  
  @override
  void initState() {
    super.initState();
    
    // Création de l'animation controller
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 15),  // Plus lent = moins de cycles de dessin
    )..repeat();
  }
  
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    
    // Initialisation des particules après que le contexte soit disponible
    if (_particles.isEmpty) {
      _initParticles();
    }
  }
  
  void _initParticles() {
    final random = Random();
    
    for (int i = 0; i < widget.particleCount; i++) {
      _particles.add(
        ParticleModel(
          position: Offset(
            random.nextDouble() * 100, 
            random.nextDouble() * 100,
          ),
          size: 1 + random.nextDouble() * widget.maxSize,
          color: _getParticleColor(i),
          speed: 0.05 + random.nextDouble() * 0.2,
          angle: random.nextDouble() * 2 * pi,
        ),
      );
    }
  }
  
  Color _getParticleColor(int index) {
    final colorType = index % 3;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    
    if (colorType == 0) {
      return isDarkMode ? AppTheme.darkPrimaryColor : AppTheme.primaryColor;
    } else if (colorType == 1) {
      return isDarkMode ? AppTheme.darkAccentColor : AppTheme.accentColor;
    } else {
      return isDarkMode 
          ? AppTheme.darkBackgroundLightColor 
          : AppTheme.backgroundLightColor;
    }
  }
  
  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return CustomPaint(
          size: Size.infinite,
          painter: ParticlesPainter(
            particles: _particles,
            progress: _animationController.value,
            opacity: widget.opacity,
          ),
        );
      },
    );
  }
}

class ParticleModel {
  final Offset position; // Position en pourcentage (0-100)
  final double size; // Taille en pixels
  final Color color; // Couleur
  final double speed; // Vitesse de déplacement
  final double angle; // Angle de déplacement
  
  ParticleModel({
    required this.position,
    required this.size,
    required this.color,
    required this.speed,
    required this.angle,
  });
}

class ParticlesPainter extends CustomPainter {
  final List<ParticleModel> particles;
  final double progress;
  final double opacity;
  
  ParticlesPainter({
    required this.particles,
    required this.progress,
    this.opacity = 0.3,
  });
  
  @override
  void paint(Canvas canvas, Size size) {
    for (final particle in particles) {
      final particleX = (particle.position.dx / 100) * size.width;
      final particleY = (particle.position.dy / 100) * size.height;
      
      // Calculer le mouvement en fonction du temps - plus lent et plus subtil
      final dx = sin(particle.angle + progress * 2 * pi) * particle.speed * 30;
      final dy = cos(particle.angle + progress * 2 * pi) * particle.speed * 30;
      
      final paint = Paint()
        ..color = particle.color.withOpacity(opacity)
        ..style = PaintingStyle.fill;
      
      // Dessiner la particule
      canvas.drawCircle(
        Offset(particleX + dx, particleY + dy),
        particle.size,
        paint,
      );
    }
  }
  
  @override
  bool shouldRepaint(ParticlesPainter oldDelegate) => 
    oldDelegate.progress != progress;
}

import React, { useEffect, useRef } from 'react';

export const AnimatedBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    // Particle nodes configuration
    const PARTICLE_COUNT = Math.min(65, Math.floor((width * height) / 22000));
    const MAX_DISTANCE = 140;

    interface Particle {
      x: number;
      y: number;
      vx: number;
      vy: number;
      radius: number;
      baseAlpha: number;
      color: string;
    }

    const colors = [
      'rgba(6, 182, 212,',   // Cyan
      'rgba(16, 185, 129,',  // Emerald
      'rgba(99, 102, 241,',  // Indigo
      'rgba(148, 163, 184,', // Slate
    ];

    const particles: Particle[] = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.45,
        vy: (Math.random() - 0.5) * 0.45,
        radius: Math.random() * 1.5 + 1,
        baseAlpha: Math.random() * 0.4 + 0.2,
        color: colors[Math.floor(Math.random() * colors.length)],
      });
    }

    // Mouse interaction
    let mouse = { x: -1000, y: -1000, radius: 160 };

    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };

    const handleMouseLeave = () => {
      mouse.x = -1000;
      mouse.y = -1000;
    };

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);
    window.addEventListener('resize', handleResize);

    // Animated Aurora Light Wave parameters
    let time = 0;

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // 1. Subtle Deep Obsidian Background
      const bgGrad = ctx.createLinearGradient(0, 0, width, height);
      bgGrad.addColorStop(0, '#040711');
      bgGrad.addColorStop(0.5, '#060a16');
      bgGrad.addColorStop(1, '#070c1a');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // 2. Animated Flowing Ambient Light Beams (Aurora effect)
      time += 0.004;
      const auroraGrad1 = ctx.createRadialGradient(
        width * 0.25 + Math.sin(time) * 120,
        height * 0.2 + Math.cos(time * 0.8) * 80,
        50,
        width * 0.25,
        height * 0.2,
        width * 0.45
      );
      auroraGrad1.addColorStop(0, 'rgba(6, 182, 212, 0.08)');
      auroraGrad1.addColorStop(0.5, 'rgba(6, 182, 212, 0.02)');
      auroraGrad1.addColorStop(1, 'transparent');
      ctx.fillStyle = auroraGrad1;
      ctx.fillRect(0, 0, width, height);

      const auroraGrad2 = ctx.createRadialGradient(
        width * 0.8 - Math.cos(time * 0.7) * 100,
        height * 0.35 + Math.sin(time * 0.9) * 90,
        50,
        width * 0.8,
        height * 0.35,
        width * 0.4
      );
      auroraGrad2.addColorStop(0, 'rgba(16, 185, 129, 0.06)');
      auroraGrad2.addColorStop(0.5, 'rgba(16, 185, 129, 0.015)');
      auroraGrad2.addColorStop(1, 'transparent');
      ctx.fillStyle = auroraGrad2;
      ctx.fillRect(0, 0, width, height);

      // 3. Update & Draw Constellation Particles & Connective Telemetry Mesh
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Move
        p.x += p.vx;
        p.y += p.vy;

        // Wrap around boundaries smoothly
        if (p.x < 0) p.x = width;
        else if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        else if (p.y > height) p.y = 0;

        // Mouse distance influence
        const dxMouse = mouse.x - p.x;
        const dyMouse = mouse.y - p.y;
        const distMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse);
        let alpha = p.baseAlpha;
        if (distMouse < mouse.radius) {
          alpha = Math.min(0.9, p.baseAlpha + (1 - distMouse / mouse.radius) * 0.6);
        }

        // Draw particle dot
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `${p.color} ${alpha})`;
        ctx.fill();

        // Connect with neighboring particles
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < MAX_DISTANCE) {
            const lineAlpha = (1 - dist / MAX_DISTANCE) * 0.15;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(148, 163, 184, ${lineAlpha})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {/* Interactive 60fps Canvas */}
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />

      {/* Ultra-fine Technical Micro-Grid Overlay */}
      <div 
        className="absolute inset-0 opacity-[0.25]"
        style={{
          backgroundImage: `linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px)`,
          backgroundSize: '40px 40px',
          maskImage: 'radial-gradient(ellipse at 50% 30%, black 50%, transparent 90%)',
          WebkitMaskImage: 'radial-gradient(ellipse at 50% 30%, black 50%, transparent 90%)'
        }}
      />

      {/* Top Subtle Cyber Horizon Line */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent" />
    </div>
  );
};

import React, { useEffect, useRef } from 'react';
import './App.css';

function App() {
  const canvasNekoRef = useRef(null);
  const canvasLunaRef = useRef(null);
  const riveInstanceNekoRef = useRef(null);
  const riveInstanceLunaRef = useRef(null);

  useEffect(() => {
    // Load Rive runtime
    if (window.rive) {
      initRiveAnimations();
    } else {
      // If Rive isn't loaded yet, wait for it
      const checkRive = setInterval(() => {
        if (window.rive) {
          clearInterval(checkRive);
          initRiveAnimations();
        }
      }, 100);
    }

    // Handle window resize
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const initRiveAnimations = () => {
    const rive = window.rive;
    const riveFile = '/anim/robots.riv';

    // Initialize Neko animation
    if (canvasNekoRef.current) {
      const canvasNeko = canvasNekoRef.current;
      const ctxNeko = canvasNeko.getContext('2d');
      const dprNeko = Math.min(window.devicePixelRatio, 1);
      
      resizeCanvas(canvasNeko, ctxNeko, dprNeko);
      
      riveInstanceNekoRef.current = new rive.Rive({
        src: riveFile,
        canvas: canvasNeko,
        autoplay: true,
        artboard: 'NekoParentLogin',
        stateMachines: 'ParentLoginState',
        fit: rive.Fit.cover,
        alignment: rive.Alignment.Center,
        onLoad: () => {
          console.log('Neko animation loaded successfully');
          
          // Try to fire the peek trigger after a short delay
          setTimeout(() => {
            triggerRiveInput('peek', riveInstanceNekoRef.current);
          }, 250);
        },
        onError: (err) => {
          console.error('Error loading Neko animation:', err);
        }
      });
    }

    // Initialize Luna animation
    if (canvasLunaRef.current) {
      const canvasLuna = canvasLunaRef.current;
      const ctxLuna = canvasLuna.getContext('2d');
      const dprLuna = Math.min(window.devicePixelRatio, 1);
      
      resizeCanvas(canvasLuna, ctxLuna, dprLuna);
      
      riveInstanceLunaRef.current = new rive.Rive({
        src: riveFile,
        canvas: canvasLuna,
        autoplay: true,
        artboard: 'LunaParentLogin',
        stateMachines: 'ParentLoginState',
        fit: rive.Fit.cover,
        alignment: rive.Alignment.Center,
        onLoad: () => {
          console.log('Luna animation loaded successfully');
          
          // Try to fire the peek trigger after a short delay
          setTimeout(() => {
            triggerRiveInput('peek', riveInstanceLunaRef.current);
          }, 250);
        },
        onError: (err) => {
          console.error('Error loading Luna animation:', err);
        }
      });
    }
  };

  const handleResize = () => {
    if (canvasNekoRef.current && canvasLunaRef.current) {
      const ctxNeko = canvasNekoRef.current.getContext('2d');
      const ctxLuna = canvasLunaRef.current.getContext('2d');
      const dpr = Math.min(window.devicePixelRatio, 1);
      
      resizeCanvas(canvasNekoRef.current, ctxNeko, dpr);
      resizeCanvas(canvasLunaRef.current, ctxLuna, dpr);
    }
  };

  const resizeCanvas = (canvas, ctx, dpr) => {
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
  };

  const triggerRiveInput = (triggerName, riveInstance) => {
    if (!riveInstance) {
      console.error('Rive instance not available');
      return false;
    }
    
    try {
      const inputs = riveInstance.stateMachineInputs('ParentLoginState');
      const trigger = inputs.find(input => input.name === triggerName);
      
      if (trigger) {
        trigger.fire();
        console.log(`Trigger fired: ${triggerName}`);
        return true;
      } else {
        console.warn(`Trigger ${triggerName} not found in inputs`);
        return false;
      }
    } catch (err) {
      console.error(`Error firing trigger ${triggerName}:`, err);
      return false;
    }
  };

  const handleNekoClick = () => {
    triggerRiveInput('wave', riveInstanceNekoRef.current);
  };

  const handleLunaClick = () => {
    triggerRiveInput('wave', riveInstanceLunaRef.current);
  };

  return (
    <>
      <div className="rive-container-neko" onClick={handleNekoClick}>
        <canvas id="rive-canvas-neko" ref={canvasNekoRef}></canvas>
      </div>

      <div className="rive-container-luna" onClick={handleLunaClick}>
        <canvas id="rive-canvas-luna" ref={canvasLunaRef}></canvas>
      </div>
      
      <div className="logo-container">
        <img src="/images/logo2.png" className="logo" alt="Wonderkid Logo" />
      </div>

      <div className="footer">
        <div className="store-button">
          <img src="/images/app-store-badge.png" id="app-store-badge" alt="Download on App Store" />
          <img src="/images/play-store-badge.png" id="play-store-badge" alt="Get it on Google Play" />
        </div>
      </div>
    </>
  );
}

export default App;

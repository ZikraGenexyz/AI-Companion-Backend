import React, { useEffect, useRef, useState } from 'react';
import { useRive, useStateMachineInput, Layout, Fit, Alignment } from '@rive-app/react-canvas';
import './App.css';

function App() {
  // For Neko animation
  const { rive: riveNeko, RiveComponent: RiveComponentNeko } = useRive({
    src: '/anim/robots.riv',
    artboard: 'NekoParentLogin',
    stateMachines: 'ParentLoginState',
    autoplay: true,
    layout: new Layout({
      fit: Fit.Cover,
      alignment: Alignment.Center,
    }),
    onLoad: () => {
      console.log('Neko animation loaded successfully');
    }
  });

  // For Luna animation
  const { rive: riveLuna, RiveComponent: RiveComponentLuna } = useRive({
    src: '/anim/robots.riv',
    artboard: 'LunaParentLogin',
    stateMachines: 'ParentLoginState',
    autoplay: true,
    layout: new Layout({
      fit: Fit.Cover,
      alignment: Alignment.Center,
    }),
    onLoad: () => {
      console.log('Luna animation loaded successfully');
    }
  });

  // Create state machine inputs for peek and wave triggers
  const peekNekoInput = useStateMachineInput(riveNeko, 'ParentLoginState', 'peek');
  const peekLunaInput = useStateMachineInput(riveLuna, 'ParentLoginState', 'peek');

  // Trigger peek animations after components load
  useEffect(() => {
    const triggerPeek = () => {
      if (peekNekoInput) {
        peekNekoInput.fire();
        console.log('Neko peek trigger fired');
      }
      
      if (peekLunaInput) {
        peekLunaInput.fire();
        console.log('Luna peek trigger fired');
      }
    };
    
    // Add a small delay to ensure the animations are ready
    const timer = setTimeout(triggerPeek, 250);
    
    return () => clearTimeout(timer);
  }, [peekNekoInput, peekLunaInput]);

  return (
    <>
      <div className="rive-container-neko">
        <RiveComponentNeko />
      </div>

      <div className="rive-container-luna">
        <RiveComponentLuna />
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

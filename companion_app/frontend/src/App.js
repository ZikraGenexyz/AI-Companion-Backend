import React, { useEffect, useRef, useState } from 'react';
import { useRive, useStateMachineInput, Layout, Fit, Alignment } from '@rive-app/react-canvas';
import './App.css';

function App() {
  // For Neko animation
  const { rive: riveNeko, RiveComponent: RiveComponentNeko } = useRive({
    src: '/anim/website2.riv',
    artboard: 'HomepageNeko',
    stateMachines: 'HomepageState',
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
    src: '/anim/website2.riv',
    artboard: 'HomepageLuna',
    stateMachines: 'HomepageState',
    autoplay: true,
    layout: new Layout({
      fit: Fit.Cover,
      alignment: Alignment.Center,
    }),
    onLoad: () => {
      console.log('Luna animation loaded successfully');
    }
  });

  // For Stars animation
  const { rive: riveStars, RiveComponent: RiveComponentStars } = useRive({
    src: '/anim/website2.riv',
    artboard: 'Stars',
    stateMachines: 'StarsState',
    autoplay: true,
    layout: new Layout({
      fit: Fit.Cover,
      alignment: Alignment.Center,
    }),
    onLoad: () => {
      console.log('Stars animation loaded successfully');
    }
  });

  // Create state machine inputs for peek and wave triggers
  const peekNekoInput = useStateMachineInput(riveNeko, 'HomepageState', 'peek');
  const peekLunaInput = useStateMachineInput(riveLuna, 'HomepageState', 'peek');

  // State for image sources
  const [appStoreImg, setAppStoreImg] = useState('/images/appstore.png');
  const [playStoreImg, setPlayStoreImg] = useState('/images/playstore.png');
  const [playStoreButtonBg, setPlayStoreButtonBg] = useState('#FFFFFF00');
  const [appStoreButtonBg, setAppStoreButtonBg] = useState('#FFFFFF00');

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
      <div className="rive-container-stars">
        <RiveComponentStars />
      </div>

      <div className="rive-container-neko">
        <RiveComponentNeko />
      </div>

      <div className="rive-container-luna">
        <RiveComponentLuna />
      </div>
      
      <div className="logo-container">
        <img src="/images/logo.png" className="logo" alt="Wonderkid Logo" />
      </div>

      <div className="footer">
        <div className="store-button-container">
          <div 
            className="store-button"
            style={{ backgroundColor: playStoreButtonBg }}
            onMouseOver={() => {
              setPlayStoreImg('/images/playstore.png');
              setAppStoreImg('/images/appstore_dark.png');
              setPlayStoreButtonBg('#FFFFFF');
              setAppStoreButtonBg('#FFFFFF00');
            }}
            onMouseOut={() => {
              setPlayStoreImg('/images/playstore.png');
              setAppStoreImg('/images/appstore.png');
              setPlayStoreButtonBg('#FFFFFF00');
              setAppStoreButtonBg('#FFFFFF00');
            }}
          >
            <img src={appStoreImg} id="app-store-badge" alt="Download on App Store" />
          </div>
          <div 
            className="store-button"
            style={{ backgroundColor: appStoreButtonBg }}
            onMouseOver={() => {
              setPlayStoreImg('/images/playstore_dark.png');
              setAppStoreImg('/images/appstore.png');
              setPlayStoreButtonBg('#FFFFFF00');
              setAppStoreButtonBg('#FFFFFF');
            }}
            onMouseOut={() => {
              setPlayStoreImg('/images/playstore.png');
              setAppStoreImg('/images/appstore.png');
              setPlayStoreButtonBg('#FFFFFF00');
              setAppStoreButtonBg('#FFFFFF00');
            }}
          >
            <img src={playStoreImg} id="play-store-badge" alt="Get it on Google Play" />
          </div>
        </div>
      </div>
    </>
  );
}

export default App;

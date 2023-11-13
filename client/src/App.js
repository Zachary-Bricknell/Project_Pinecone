import React, { useState } from 'react';
import './App.css';
import PointCloudViewer from './components/PointCloudViewer';

const App = () => {
  const [cameraConfig, setCameraConfig] = useState({
    position: [0, 0, 5],
    lookAt: [0, 0, 0],
    fov: 75, // Default fov
  });

  const handleCameraChange = (view) => {
    const configs = {
      //temporary, Does not work very well but it does do stuff for now. 
      front: { position: [0, 0, 10], lookAt: [0, 0, 0], fov: 110 }, 
      rear: { position: [0, 0, -10], lookAt: [0, 0, 0], fov: 110 },
      top: { position: [0, 10, 0], lookAt: [0, 0, 0], fov: 110 },
      bottom: { position: [0, -10, 0], lookAt: [0, 0, 0], fov: 110 },
    };
    setCameraConfig(configs[view]);
  };

  return (
    <div className="App">
      <div className="header">
        <h1>Project Pinecone</h1>
        <h2>Title</h2>
      </div>
      <div className="container">
        <div className="menu-box">
          <button onClick={() => handleCameraChange('front')}>Front</button>
          <button onClick={() => handleCameraChange('rear')}>Rear</button>
          <button onClick={() => handleCameraChange('top')}>Top</button>
          <button onClick={() => handleCameraChange('bottom')}>Bottom</button>
        </div>
        <div className="lidar-area">
          <PointCloudViewer cameraConfig={cameraConfig} />
        </div>
      </div>
    </div>
  );
};

export default App;

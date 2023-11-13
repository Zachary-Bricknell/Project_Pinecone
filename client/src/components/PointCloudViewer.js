import React from 'react';
import { Canvas } from '@react-three/fiber';
import PointCloud from './PointCloud';
import CameraControls from './CameraControls';

const PointCloudViewer = ({ cameraConfig }) => {
  return (
    <div className="canvas-container">
      <Canvas style={{ background: 'black' }}>
        <ambientLight intensity={0.5} />
        <PointCloud url='/sample1.ply' />
        <CameraControls cameraPosition={cameraConfig.position} cameraLookAt={cameraConfig.lookAt} fov={cameraConfig.fov} />
      </Canvas>
    </div>
  );
};

export default PointCloudViewer;

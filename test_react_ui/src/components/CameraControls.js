import React, { useRef, useEffect } from 'react';
import { useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

const CameraControls = ({ cameraPosition, cameraLookAt, fov = 75 }) => { 
  const controls = useRef();
  const { camera } = useThree();

  useEffect(() => {
    camera.position.set(...cameraPosition);
    camera.lookAt(...cameraLookAt);
    camera.fov = fov;
    camera.updateProjectionMatrix(); 
    controls.current.update();
  }, [camera, cameraPosition, cameraLookAt, fov]);

  return <OrbitControls ref={controls} />;
};

export default CameraControls;

import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader';

export default function PointCloud({ url }) {
  const mesh = useRef();
  const [geometry, setGeometry] = useState();

  useEffect(() => {
    const loader = new PLYLoader();
    loader.load(url, (geom) => {
      setGeometry(geom);
    });
  }, [url]);

useEffect(() => {
  const loader = new PLYLoader();
  loader.load(url, (geom) => {

    const scale = 1; // for the point size, sometimes came up at giant cubes

    geom.scale(scale, scale, scale);
    geom.center();
    setGeometry(geom);
  });
}, [url]);

return geometry ? (
  <points ref={mesh} geometry={geometry}>
    <pointsMaterial color={'white'} size={0.01} />
  </points>
) : null;

}

import React, { useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { getDropTraits } from '../traits/api';

type Props = { dropId: string };

function parseGlowColor(value?: string): number {
  if (!value) return 0xffaa00;
  try {
    return new THREE.Color(value).getHex();
  } catch {
    return 0xffaa00;
  }
}

export const ThreeGlowDemo: React.FC<Props> = ({ dropId }) => {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [colorHex, setColorHex] = useState<number>(0xffaa00);
  const [hasGlow, setHasGlow] = useState<boolean>(false);

  useEffect(() => {
    getDropTraits(dropId).then((traits) => {
      const glowTrait = traits.find((t) => t.game_effects?.unity_webgl && (t.game_effects.unity_webgl as any).glow);
      const glow = glowTrait ? (glowTrait.game_effects!.unity_webgl as any).glow as string : undefined;
      setHasGlow(Boolean(glow));
      setColorHex(parseGlowColor(glow));
    });
  }, [dropId]);

  useEffect(() => {
    if (!mountRef.current) return;
    const width = mountRef.current.clientWidth || 400;
    const height = 300;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.z = 5;
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    mountRef.current.appendChild(renderer.domElement);

    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshStandardMaterial({ color: 0x333333, emissive: hasGlow ? colorHex : 0x000000, emissiveIntensity: hasGlow ? 1.0 : 0.0 });
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);

    const light = new THREE.PointLight(0xffffff, 1, 100);
    light.position.set(5, 5, 5);
    scene.add(light);

    let animId = 0;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      cube.rotation.x += 0.01;
      cube.rotation.y += 0.01;
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(animId);
      renderer.dispose();
      geometry.dispose();
      (material as THREE.Material).dispose();
      if (renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
    };
  }, [colorHex, hasGlow]);

  return (
    <div>
      <h2 className="text-lg font-semibold mb-2">Three.js Glow Demo</h2>
      <div ref={mountRef} style={{ width: '100%', maxWidth: 600 }} />
      {!hasGlow && <div className="text-gray-500 mt-2">No Unity glow trait found for this drop.</div>}
    </div>
  );
};

export default ThreeGlowDemo;

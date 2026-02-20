import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Text, Html, MeshTransmissionMaterial, Float, Trail } from '@react-three/drei';
import * as THREE from 'three';

// 1. The "Agent" Node (Glassy Geometric Shape)
const AgentNode = ({ position, color, label, isActive, isCompleted }) => {
  const meshRef = useRef();
  
  // Rotate the node slowly
  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += delta * 0.2;
      meshRef.current.rotation.y += delta * 0.3;
    }
  });

  return (
    <group position={position}>
      <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
        <mesh ref={meshRef} scale={isActive ? 1.2 : 1}>
          <icosahedronGeometry args={[1, 0]} /> {/* Geometric "AI" look */}
          
          {/* Glassy/Pastel Material */}
          <MeshTransmissionMaterial
            backside
            samples={4}
            thickness={0.5}
            chromaticAberration={0.1}
            anisotropy={0.1}
            distortion={0.1}
            distortionScale={0.1}
            temporalDistortion={0.1}
            color={isActive ? color : isCompleted ? '#10B981' : '#CBD5E1'}
            emissive={isActive ? color : '#000000'}
            emissiveIntensity={isActive ? 0.5 : 0}
            roughness={0.2}
            metalness={0.1}
          />
        </mesh>
      </Float>

      {/* Label underneath */}
      <Html position={[0, -1.8, 0]} center transform sprite>
        <div className={`px-3 py-1 rounded-full text-xs font-bold border transition-all duration-500 whitespace-nowrap ${
          isActive 
            ? 'bg-white text-slate-800 border-blue-400 shadow-lg scale-110' 
            : isCompleted
            ? 'bg-emerald-50 text-emerald-600 border-emerald-200'
            : 'bg-slate-50/50 text-slate-400 border-slate-200'
        }`}>
          {label}
        </div>
      </Html>
    </group>
  );
};

// 2. The "Data Packet" (Glowing Orb traveling between nodes)
const DataPacket = ({ step }) => {
  const ref = useRef();
  const [target, setTarget] = useState(new THREE.Vector3(-4, 0, 0));

  useEffect(() => {
    // Map steps to physical positions in the 3D scene
    if (step === 'gatekeeper') setTarget(new THREE.Vector3(-4, 0, 0));
    if (step === 'validator') setTarget(new THREE.Vector3(0, 0, 0));
    if (step === 'inquisitor') setTarget(new THREE.Vector3(4, 0, 0));
  }, [step]);

  useFrame((state, delta) => {
    // Smoothly lerp (move) the packet to the target position
    if (ref.current) {
      ref.current.position.lerp(target, delta * 2);
    }
  });

  return (
    <Trail width={2} length={6} color="#FBBF24" attenuation={(t) => t * t}>
      <mesh ref={ref} position={[-6, 0, 0]}>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshBasicMaterial color="#FBBF24" toneMapped={false} />
        <pointLight intensity={2} distance={3} color="#FBBF24" />
      </mesh>
    </Trail>
  );
};

// 3. The Main Scene
const Pipeline3D = ({ currentStep }) => {
  // Logic to determine which node is active/completed
  const getStatus = (nodeName) => {
    const sequence = ['idle', 'gatekeeper', 'validator', 'inquisitor', 'done'];
    const nodeIndex = sequence.indexOf(nodeName);
    const currentIndex = sequence.indexOf(currentStep);
    
    if (currentIndex === nodeIndex) return 'active';
    if (currentIndex > nodeIndex) return 'completed';
    return 'idle';
  };

  return (
    <div className="h-[400px] w-full bg-gradient-to-b from-blue-50/50 to-white rounded-3xl overflow-hidden border border-white shadow-inner">
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        {/* Soft Studio Lighting for Pastel Look */}
        <ambientLight intensity={0.7} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} color="#ffffff" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#38BDF8" />

        <group position={[0, 0.5, 0]}>
          {/* The 3 Agents positioned in space */}
          <AgentNode 
            position={[-4, 0, 0]} 
            color="#38BDF8" // Pastel Blue
            label="Gatekeeper (PII)" 
            isActive={getStatus('gatekeeper') === 'active'}
            isCompleted={getStatus('gatekeeper') === 'completed'}
          />
          
          <AgentNode 
            position={[0, 0, 0]} 
            color="#A78BFA" // Pastel Purple
            label="Validator (Skills)" 
            isActive={getStatus('validator') === 'active'}
            isCompleted={getStatus('validator') === 'completed'}
          />
          
          <AgentNode 
            position={[4, 0, 0]} 
            color="#FB923C" // Pastel Orange
            label="Inquisitor (Fraud)" 
            isActive={getStatus('inquisitor') === 'active'}
            isCompleted={getStatus('inquisitor') === 'completed'}
          />

          {/* Connectors (Lines between agents) */}
          <mesh position={[-2, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.05, 0.05, 4]} />
            <meshBasicMaterial color="#E2E8F0" transparent opacity={0.5} />
          </mesh>
          <mesh position={[2, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.05, 0.05, 4]} />
            <meshBasicMaterial color="#E2E8F0" transparent opacity={0.5} />
          </mesh>

          {/* Moving Packet */}
          {currentStep !== 'idle' && currentStep !== 'done' && (
            <DataPacket step={currentStep} />
          )}
        </group>
      </Canvas>
    </div>
  );
};

export default Pipeline3D;

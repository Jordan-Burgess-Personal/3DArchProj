import { Canvas } from '@react-three/fiber'
import { OrbitControls, Grid, Text } from '@react-three/drei'
import { useArchitectureStore } from '../store/architectureStore'

function Node({ component }) {
  const select = useArchitectureStore((s) => s.select)
  const colorMap = { frontend: '#14b8a6', backend: '#2563eb', database: '#7c3aed', auth: '#db2777', cache: '#f59e0b' }
  const color = colorMap[component.type] || '#475569'
  return (
    <group position={[component.position.x, component.position.y, component.position.z]} onClick={() => select(component.id)}>
      <mesh>
        <boxGeometry args={[1.7, 1, 1]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <Text position={[0, 0.7, 0]} fontSize={0.18} anchorX="center" anchorY="middle">
        {component.name}
      </Text>
    </group>
  )
}

export default function ArchitectureCanvas() {
  const model = useArchitectureStore((s) => s.model)
  return (
    <Canvas camera={{ position: [0, 5, 7], fov: 50 }}>
      <ambientLight intensity={0.8} />
      <directionalLight position={[5, 8, 5]} intensity={1} />
      <Grid infiniteGrid />
      {model.components.map((component) => <Node key={component.id} component={component} />)}
      <OrbitControls />
    </Canvas>
  )
}

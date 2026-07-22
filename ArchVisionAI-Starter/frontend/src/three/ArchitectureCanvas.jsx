import { useMemo, useState } from 'react'
import {
  Grid,
  Line,
  OrbitControls,
  Text,
} from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import * as THREE from 'three'

import { findComponentTemplate } from '../config/architectureCatalog'
import { useArchitectureStore } from '../store/architectureStore'

const NODE_SIZE = {
  width: 1.9,
  height: 1,
  depth: 1.2,
}

function snap(value, increment = 0.5) {
  return (
    Math.round(value / increment) *
    increment
  )
}

function getPosition(component) {
  return [
    component.position?.x ?? 0,
    component.position?.y ?? 0.6,
    component.position?.z ?? 0,
  ]
}

function midpoint(first, second) {
  return [
    (first[0] + second[0]) / 2,
    (first[1] + second[1]) / 2 + 0.25,
    (first[2] + second[2]) / 2,
  ]
}

function ConnectionLine({
  connection,
  components,
  selected = false,
  preview = false,
  onSelect,
}) {
  const source = components.find(
    (component) =>
      component.id === connection.source,
  )

  const target = components.find(
    (component) =>
      component.id === connection.target,
  )

  if (!source || !target) {
    return null
  }

  const sourcePosition = getPosition(source)
  const targetPosition = getPosition(target)
  const labelPosition = midpoint(
    sourcePosition,
    targetPosition,
  )

  const visibleColor = preview
    ? '#facc15'
    : selected
      ? '#22d3ee'
      : '#818cf8'

  function handleConnectionClick(event) {
    if (preview) {
      return
    }

    event.stopPropagation()
    onSelect(connection.id)
  }

  return (
    <group>
      {/* Wide transparent hit target */}
      {!preview && (
        <Line
          points={[
            sourcePosition,
            targetPosition,
          ]}
          color="#ffffff"
          transparent
          opacity={0}
          lineWidth={14}
          onClick={handleConnectionClick}
        />
      )}

      <Line
        points={[
          sourcePosition,
          targetPosition,
        ]}
        color={visibleColor}
        lineWidth={
          preview || selected ? 4 : 2
        }
        dashed={preview}
        dashSize={0.3}
        gapSize={0.2}
        onClick={handleConnectionClick}
      />

      {!preview && (
        <Text
          position={labelPosition}
          fontSize={0.14}
          anchorX="center"
          anchorY="middle"
          color={
            selected
              ? '#67e8f9'
              : '#c7d2fe'
          }
          outlineWidth={0.008}
          outlineColor="#020617"
          onClick={handleConnectionClick}
        >
          {connection.label ||
            connection.connectionType}
        </Text>
      )}
    </group>
  )
}

function Node({
  component,
  selected,
  connectionSource,
  connectionTarget,
  dragging,
  onPointerDown,
  onClick,
}) {
  const baseColor =
    component.color || '#475569'

  return (
    <group position={getPosition(component)}>
      <mesh
        castShadow
        receiveShadow
        onPointerDown={(event) => {
          event.stopPropagation()
          onPointerDown(
            event,
            component.id,
          )
        }}
        onClick={(event) => {
          event.stopPropagation()
          onClick(component.id)
        }}
      >
        <boxGeometry
          args={[
            NODE_SIZE.width,
            NODE_SIZE.height,
            NODE_SIZE.depth,
          ]}
        />

        <meshStandardMaterial
          color={baseColor}
          emissive={
            selected ||
            connectionSource ||
            connectionTarget ||
            dragging
              ? new THREE.Color(baseColor)
              : new THREE.Color(
                  '#000000',
                )
          }
          emissiveIntensity={
            connectionSource
              ? 0.6
              : connectionTarget
                ? 0.4
                : selected || dragging
                  ? 0.25
                  : 0
          }
          roughness={0.5}
          metalness={0.1}
        />
      </mesh>

      <Text
        position={[0, 0.72, 0]}
        fontSize={0.18}
        anchorX="center"
        anchorY="middle"
        color={
          connectionSource
            ? '#facc15'
            : connectionTarget
              ? '#a5b4fc'
              : '#ffffff'
        }
      >
        {component.name}
      </Text>
    </group>
  )
}

function WorkspaceScene() {
  const model = useArchitectureStore(
    (state) => state.model,
  )

  const selectedId = useArchitectureStore(
    (state) => state.selectedId,
  )

  const selectedConnectionId =
    useArchitectureStore(
      (state) =>
        state.selectedConnectionId,
    )

  const activeComponentTemplateId =
    useArchitectureStore(
      (state) =>
        state.activeComponentTemplateId,
    )

  const activeConnectionTemplateId =
    useArchitectureStore(
      (state) =>
        state.activeConnectionTemplateId,
    )

  const connectionSourceId =
    useArchitectureStore(
      (state) =>
        state.connectionSourceId,
    )

  const connectionTargetIds =
    useArchitectureStore(
      (state) =>
        state.connectionTargetIds,
    )

  const isDraggingComponent =
    useArchitectureStore(
      (state) =>
        state.isDraggingComponent,
    )

  const select = useArchitectureStore(
    (state) => state.select,
  )

  const selectConnection =
    useArchitectureStore(
      (state) =>
        state.selectConnection,
    )

  const clearSelection =
    useArchitectureStore(
      (state) =>
        state.clearSelection,
    )

  const placeComponent =
    useArchitectureStore(
      (state) =>
        state.placeComponent,
    )

  const moveComponent =
    useArchitectureStore(
      (state) =>
        state.moveComponent,
    )

  const clearComponentPlacement =
    useArchitectureStore(
      (state) =>
        state.clearComponentPlacement,
    )

  const clearConnectionTemplate =
    useArchitectureStore(
      (state) =>
        state.clearConnectionTemplate,
    )

  const beginConnection =
    useArchitectureStore(
      (state) =>
        state.beginConnection,
    )

  const toggleConnectionTarget =
    useArchitectureStore(
      (state) =>
        state.toggleConnectionTarget,
    )

  const cancelConnectionBuilder =
    useArchitectureStore(
      (state) =>
        state.cancelConnectionBuilder,
    )

  const setDraggingComponent =
    useArchitectureStore(
      (state) =>
        state.setDraggingComponent,
    )

  const [
    draggedComponentId,
    setDraggedComponentId,
  ] = useState(null)

  const [
    hoverPosition,
    setHoverPosition,
  ] = useState(null)

  const activeComponentTemplate =
    useMemo(
      () =>
        activeComponentTemplateId
          ? findComponentTemplate(
              activeComponentTemplateId,
            )
          : null,
      [activeComponentTemplateId],
    )

  function canvasPosition(
    point,
    y = 0.6,
  ) {
    return {
      x: snap(point.x),
      y,
      z: snap(point.z),
    }
  }

  function handleNodeClick(componentId) {
    if (activeConnectionTemplateId) {
      if (!connectionSourceId) {
        beginConnection(componentId)
        return
      }

      if (
        componentId !==
        connectionSourceId
      ) {
        toggleConnectionTarget(
          componentId,
        )
      }

      return
    }

    if (!activeComponentTemplate) {
      select(componentId)
    }
  }

  function handleNodePointerDown(
    event,
    componentId,
  ) {
    if (
      event.button !== 0 ||
      activeComponentTemplate ||
      activeConnectionTemplateId
    ) {
      return
    }

    setDraggedComponentId(componentId)
    setDraggingComponent(true)
    select(componentId)
  }

  function handleGroundPointerMove(
    event,
  ) {
    event.stopPropagation()

    const position = canvasPosition(
      event.point,
    )

    if (draggedComponentId) {
      const component =
        model.components.find(
          (item) =>
            item.id ===
            draggedComponentId,
        )

      moveComponent(
        draggedComponentId,
        {
          ...position,
          y:
            component?.position?.y ??
            0.6,
        },
      )

      return
    }

    if (activeComponentTemplate) {
      setHoverPosition(position)
    }
  }

  function handleGroundClick(event) {
    event.stopPropagation()

    if (event.button !== 0) {
      return
    }

    if (activeComponentTemplate) {
      placeComponent(
        activeComponentTemplate,
        canvasPosition(event.point),
      )

      return
    }

    if (!activeConnectionTemplateId) {
      clearSelection()
    }
  }

  function handleGroundPointerUp(
    event,
  ) {
    event.stopPropagation()

    setDraggedComponentId(null)
    setDraggingComponent(false)
  }

  function handleContextMenu(event) {
    event.stopPropagation()
    event.nativeEvent.preventDefault()

    clearComponentPlacement()
    clearConnectionTemplate()
    cancelConnectionBuilder()

    setDraggedComponentId(null)
    setDraggingComponent(false)
    setHoverPosition(null)
  }

  const controlsEnabled =
    !activeComponentTemplate &&
    !activeConnectionTemplateId &&
    !isDraggingComponent

  return (
    <>
      <ambientLight intensity={0.85} />

      <directionalLight
        castShadow
        position={[7, 10, 6]}
        intensity={1.25}
      />

      <directionalLight
        position={[-5, 4, -4]}
        intensity={0.3}
      />

      <Grid
        infiniteGrid
        cellSize={1}
        cellThickness={0.6}
        cellColor="#0369a1"
        sectionSize={5}
        sectionThickness={1.2}
        sectionColor="#0284c7"
        fadeDistance={70}
        fadeStrength={1}
      />

      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.01, 0]}
        onPointerMove={
          handleGroundPointerMove
        }
        onPointerUp={
          handleGroundPointerUp
        }
        onClick={handleGroundClick}
        onContextMenu={
          handleContextMenu
        }
      >
        <planeGeometry
          args={[200, 200]}
        />

        <meshBasicMaterial
          transparent
          opacity={0}
          depthWrite={false}
        />
      </mesh>

      {model.connections.map(
        (connection) => (
          <ConnectionLine
            key={connection.id}
            connection={connection}
            components={
              model.components
            }
            selected={
              selectedConnectionId ===
              connection.id
            }
            onSelect={
              selectConnection
            }
          />
        ),
      )}

      {connectionSourceId &&
        connectionTargetIds.map(
          (targetId) => (
            <ConnectionLine
              key={`preview-${connectionSourceId}-${targetId}`}
              connection={{
                source:
                  connectionSourceId,
                target: targetId,
              }}
              components={
                model.components
              }
              preview
              onSelect={() => {}}
            />
          ),
        )}

      {model.components.map(
        (component) => (
          <Node
            key={component.id}
            component={component}
            selected={
              selectedId ===
              component.id
            }
            connectionSource={
              connectionSourceId ===
              component.id
            }
            connectionTarget={connectionTargetIds.includes(
              component.id,
            )}
            dragging={
              draggedComponentId ===
              component.id
            }
            onPointerDown={
              handleNodePointerDown
            }
            onClick={
              handleNodeClick
            }
          />
        ),
      )}

      {activeComponentTemplate &&
        hoverPosition && (
          <group
            position={[
              hoverPosition.x,
              hoverPosition.y,
              hoverPosition.z,
            ]}
          >
            <mesh>
              <boxGeometry
                args={[
                  NODE_SIZE.width,
                  NODE_SIZE.height,
                  NODE_SIZE.depth,
                ]}
              />

              <meshStandardMaterial
                color={
                  activeComponentTemplate.color ||
                  '#6366f1'
                }
                transparent
                opacity={0.4}
                depthWrite={false}
              />
            </mesh>

            <Text
              position={[0, 0.72, 0]}
              fontSize={0.16}
              anchorX="center"
              anchorY="middle"
              color="#ffffff"
            >
              {`Place ${activeComponentTemplate.name}`}
            </Text>
          </group>
        )}

      <OrbitControls
        enabled={controlsEnabled}
        makeDefault
      />
    </>
  )
}

export default function ArchitectureCanvas() {
  return (
    <div
      className="h-full w-full bg-slate-950"
      onContextMenu={(event) =>
        event.preventDefault()
      }
    >
      <Canvas
        shadows
        camera={{
          position: [0, 6, 9],
          fov: 50,
          near: 0.1,
          far: 500,
        }}
      >
        <color
          attach="background"
          args={['#020617']}
        />

        <WorkspaceScene />
      </Canvas>
    </div>
  )
}
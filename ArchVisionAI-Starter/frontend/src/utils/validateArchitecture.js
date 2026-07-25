const VALID_COMPONENT_TYPES = new Set([
  'frontend',
  'mobile',
  'backend',
  'worker',
  'database',
  'cache',
  'storage',
  'auth',
  'authorization',
  'external_api',
  'message_queue',
  'load_balancer',
  'gateway',
  'service',
  'ai_service',
  'cloud',
  'container',
  'custom',
])

function isObject(value) {
  return (
    value !== null &&
    typeof value === 'object' &&
    !Array.isArray(value)
  )
}

function isNonEmptyString(value) {
  return (
    typeof value === 'string' &&
    value.trim().length > 0
  )
}

function isFiniteNumber(value) {
  return (
    typeof value === 'number' &&
    Number.isFinite(value)
  )
}

function itemLabel(type, item, index) {
  if (isNonEmptyString(item?.id)) {
    return `${type} "${item.id.trim()}"`
  }

  return `${type} at index ${index}`
}

export function validateArchitecture(architecture) {
  const errors = []

  if (!isObject(architecture)) {
    return {
      valid: false,
      errors: [
        'Architecture must be a JSON object.',
      ],
    }
  }

  if (!isNonEmptyString(architecture.name)) {
    errors.push(
      'Architecture name is required.',
    )
  }

  if (!Array.isArray(architecture.components)) {
    errors.push(
      'Architecture components must be an array.',
    )
  }

  if (!Array.isArray(architecture.connections)) {
    errors.push(
      'Architecture connections must be an array.',
    )
  }

  if (errors.length > 0) {
    return {
      valid: false,
      errors,
    }
  }

  const componentIds = new Set()

  architecture.components.forEach(
    (component, index) => {
      const label = itemLabel(
        'Component',
        component,
        index,
      )

      if (!isObject(component)) {
        errors.push(
          `Component at index ${index} must be an object.`,
        )
        return
      }

      if (!isNonEmptyString(component.id)) {
        errors.push(
          `${label} is missing a valid id.`,
        )
      } else {
        const componentId = component.id.trim()

        if (componentIds.has(componentId)) {
          errors.push(
            `Component ID "${componentId}" is duplicated.`,
          )
        }

        componentIds.add(componentId)
      }

      if (!isNonEmptyString(component.type)) {
        errors.push(
          `${label} is missing a valid type.`,
        )
      } else if (
        !VALID_COMPONENT_TYPES.has(
          component.type.trim(),
        )
      ) {
        errors.push(
          `${label} has unsupported type "${component.type}".`,
        )
      }

      if (!isNonEmptyString(component.name)) {
        errors.push(
          `${label} is missing a valid name.`,
        )
      }

      if (!isObject(component.position)) {
        errors.push(
          `${label} is missing a valid position object.`,
        )
      } else {
        ;['x', 'y', 'z'].forEach((axis) => {
          if (
            !isFiniteNumber(
              component.position[axis],
            )
          ) {
            errors.push(
              `${label} position.${axis} must be a finite number.`,
            )
          }
        })
      }

      if (
        component.metadata !== undefined &&
        !isObject(component.metadata)
      ) {
        errors.push(
          `${label} metadata must be an object.`,
        )
      }
    },
  )

  const connectionIds = new Set()

  architecture.connections.forEach(
    (connection, index) => {
      const label = itemLabel(
        'Connection',
        connection,
        index,
      )

      if (!isObject(connection)) {
        errors.push(
          `Connection at index ${index} must be an object.`,
        )
        return
      }

      if (!isNonEmptyString(connection.id)) {
        errors.push(
          `${label} is missing a valid id.`,
        )
      } else {
        const connectionId =
          connection.id.trim()

        if (
          connectionIds.has(connectionId)
        ) {
          errors.push(
            `Connection ID "${connectionId}" is duplicated.`,
          )
        }

        connectionIds.add(connectionId)
      }

      if (!isNonEmptyString(connection.source)) {
        errors.push(
          `${label} is missing a valid source.`,
        )
      }

      if (!isNonEmptyString(connection.target)) {
        errors.push(
          `${label} is missing a valid target.`,
        )
      }

      const connectionType =
        connection.connectionType ??
        connection.connection_type

      if (!isNonEmptyString(connectionType)) {
        errors.push(
          `${label} is missing a valid connection type.`,
        )
      }

      const source = isNonEmptyString(
        connection.source,
      )
        ? connection.source.trim()
        : null

      const target = isNonEmptyString(
        connection.target,
      )
        ? connection.target.trim()
        : null

      if (source && target && source === target) {
        errors.push(
          `${label} cannot connect a component to itself.`,
        )
      }

      if (
        source &&
        !componentIds.has(source)
      ) {
        errors.push(
          `${label} references unknown source component "${source}".`,
        )
      }

      if (
        target &&
        !componentIds.has(target)
      ) {
        errors.push(
          `${label} references unknown target component "${target}".`,
        )
      }

      if (
        connection.metadata !== undefined &&
        !isObject(connection.metadata)
      ) {
        errors.push(
          `${label} metadata must be an object.`,
        )
      }
    },
  )

  return {
    valid: errors.length === 0,
    errors,
  }
}

export function assertValidArchitecture(
  architecture,
  message =
    'The architecture failed validation.',
) {
  const validation =
    validateArchitecture(architecture)

  if (!validation.valid) {
    const error = new Error(message)
    error.name =
      'ArchitectureValidationError'
    error.validationErrors =
      validation.errors

    throw error
  }

  return architecture
}

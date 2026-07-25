import {
  describe,
  expect,
  it,
} from 'vitest'

import {
  assertValidArchitecture,
  validateArchitecture,
} from './validateArchitecture'

function validArchitecture() {
  return {
    name: 'Valid Architecture',
    description: '',
    components: [
      {
        id: 'frontend',
        type: 'frontend',
        name: 'React Frontend',
        position: {
          x: -4,
          y: 0.5,
          z: 0,
        },
        metadata: {},
      },
      {
        id: 'backend',
        type: 'backend',
        name: 'FastAPI Backend',
        position: {
          x: 0,
          y: 0.5,
          z: 0,
        },
        metadata: {},
      },
    ],
    connections: [
      {
        id: 'frontend-backend',
        source: 'frontend',
        target: 'backend',
        connection_type: 'rest_api',
        metadata: {},
      },
    ],
  }
}

describe('validateArchitecture', () => {
  it('accepts a valid architecture', () => {
    const result =
      validateArchitecture(
        validArchitecture(),
      )

    expect(result.valid).toBe(true)
    expect(result.errors).toEqual([])
  })

  it('rejects a missing components array', () => {
    const architecture =
      validArchitecture()

    delete architecture.components

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Architecture components must be an array.',
    )
  })

  it('rejects a missing connections array', () => {
    const architecture =
      validArchitecture()

    delete architecture.connections

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Architecture connections must be an array.',
    )
  })

  it('rejects duplicate component IDs', () => {
    const architecture =
      validArchitecture()

    architecture.components[1].id =
      'frontend'

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Component ID "frontend" is duplicated.',
    )
  })

  it('rejects malformed positions', () => {
    const architecture =
      validArchitecture()

    architecture.components[0].position.x =
      'left'

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Component "frontend" position.x must be a finite number.',
    )
  })

  it('rejects missing connection endpoints', () => {
    const architecture =
      validArchitecture()

    architecture.connections[0].source =
      ''

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Connection "frontend-backend" is missing a valid source.',
    )
  })

  it('rejects references to unknown components', () => {
    const architecture =
      validArchitecture()

    architecture.connections[0].target =
      'missing-database'

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Connection "frontend-backend" references unknown target component "missing-database".',
    )
  })

  it('rejects self-connections', () => {
    const architecture =
      validArchitecture()

    architecture.connections[0].target =
      'frontend'

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Connection "frontend-backend" cannot connect a component to itself.',
    )
  })

  it('rejects a non-object architecture', () => {
    const result = validateArchitecture(null)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Architecture must be a JSON object.',
    )
  })

  it('rejects an array passed as the architecture', () => {
    const result = validateArchitecture([])

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Architecture must be a JSON object.',
    )
  })

  it('rejects an unsupported component type', () => {
    const architecture =
      validArchitecture()

    architecture.components[0].type =
      'blockchain'

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Component "frontend" has unsupported type "blockchain".',
    )
  })

  it('rejects duplicate connection IDs', () => {
    const architecture =
      validArchitecture()

    architecture.connections.push({
      id: 'frontend-backend',
      source: 'backend',
      target: 'frontend',
      connection_type: 'rest_api',
      metadata: {},
    })

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Connection ID "frontend-backend" is duplicated.',
    )
  })

  it('rejects a connection missing a connection type', () => {
    const architecture =
      validArchitecture()

    delete architecture.connections[0]
      .connection_type

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Connection "frontend-backend" is missing a valid connection type.',
    )
  })

  it('accepts connectionType as an alias for connection_type', () => {
    const architecture =
      validArchitecture()

    delete architecture.connections[0]
      .connection_type
    architecture.connections[0].connectionType =
      'rest_api'

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(true)
    expect(result.errors).toEqual([])
  })

  it('rejects references to unknown source components', () => {
    const architecture =
      validArchitecture()

    architecture.connections[0].source =
      'missing-gateway'

    const result =
      validateArchitecture(architecture)

    expect(result.valid).toBe(false)
    expect(result.errors).toContain(
      'Connection "frontend-backend" references unknown source component "missing-gateway".',
    )
  })
})

describe('assertValidArchitecture', () => {
  it('returns the architecture unchanged when valid', () => {
    const architecture = validArchitecture()

    const result =
      assertValidArchitecture(architecture)

    expect(result).toBe(architecture)
  })

  it('throws a named ArchitectureValidationError when invalid', () => {
    const architecture =
      validArchitecture()

    architecture.components[1].id =
      'frontend'

    expect(() =>
      assertValidArchitecture(architecture),
    ).toThrow()

    try {
      assertValidArchitecture(architecture)
    } catch (error) {
      expect(error.name).toBe(
        'ArchitectureValidationError',
      )
      expect(error.validationErrors).toContain(
        'Component ID "frontend" is duplicated.',
      )
    }
  })

  it('uses the provided message on the thrown error', () => {
    const architecture =
      validArchitecture()

    delete architecture.connections

    expect(() =>
      assertValidArchitecture(
        architecture,
        'Custom failure message.',
      ),
    ).toThrow('Custom failure message.')
  })
})

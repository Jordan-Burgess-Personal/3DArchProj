import {
  Bot,
  Box,
  Braces,
  Cloud,
  Database,
  ExternalLink,
  Globe,
  HardDrive,
  KeyRound,
  Layers3,
  Network,
  Server,
  ShieldCheck,
  Smartphone,
  Workflow,
} from 'lucide-react'

export const componentCategories = [
  {
    id: 'client',
    label: 'Client Applications',
    items: [
      {
        id: 'web-frontend',
        category: 'client',
        type: 'frontend',
        name: 'Web Frontend',
        technology: 'React',
        description: 'Browser-based user interface.',
        color: '#0d9488',
        icon: Globe,
      },
      {
        id: 'mobile-client',
        category: 'client',
        type: 'mobile',
        name: 'Mobile Application',
        technology: 'React Native',
        description: 'Mobile client application.',
        color: '#0891b2',
        icon: Smartphone,
      },
    ],
  },
  {
    id: 'application',
    label: 'Application Services',
    items: [
      {
        id: 'api-service',
        category: 'application',
        type: 'backend',
        name: 'API Service',
        technology: 'FastAPI',
        description: 'Backend API and business-logic service.',
        color: '#1d4ed8',
        icon: Server,
      },
      {
        id: 'background-worker',
        category: 'application',
        type: 'worker',
        name: 'Background Worker',
        technology: 'Python',
        description: 'Processes asynchronous background jobs.',
        color: '#7c3aed',
        icon: Workflow,
      },
      {
        id: 'ai-service',
        category: 'application',
        type: 'ai-service',
        name: 'AI Service',
        technology: 'OpenAI',
        description: 'AI-powered generation or analysis service.',
        color: '#c026d3',
        icon: Bot,
      },
    ],
  },
  {
    id: 'data',
    label: 'Data and Storage',
    items: [
      {
        id: 'relational-database',
        category: 'data',
        type: 'database',
        name: 'Relational Database',
        technology: 'PostgreSQL',
        description: 'Structured relational data storage.',
        color: '#6d28d9',
        icon: Database,
      },
      {
        id: 'document-database',
        category: 'data',
        type: 'document-database',
        name: 'Document Database',
        technology: 'MongoDB',
        description: 'Document-oriented data storage.',
        color: '#15803d',
        icon: Layers3,
      },
      {
        id: 'object-storage',
        category: 'data',
        type: 'object-storage',
        name: 'Object Storage',
        technology: 'S3-compatible storage',
        description: 'File and object storage service.',
        color: '#b45309',
        icon: HardDrive,
      },
    ],
  },
  {
    id: 'infrastructure',
    label: 'Infrastructure',
    items: [
      {
        id: 'container',
        category: 'infrastructure',
        type: 'container',
        name: 'Container',
        technology: 'Docker',
        description: 'Containerized application runtime.',
        color: '#0369a1',
        icon: Box,
      },
      {
        id: 'cloud-service',
        category: 'infrastructure',
        type: 'cloud',
        name: 'Cloud Service',
        technology: 'Cloud Platform',
        description: 'Cloud-hosted application resource.',
        color: '#2563eb',
        icon: Cloud,
      },
      {
        id: 'gateway',
        category: 'infrastructure',
        type: 'gateway',
        name: 'API Gateway',
        technology: 'API Gateway',
        description: 'Routes and manages external API traffic.',
        color: '#be123c',
        icon: Network,
      },
    ],
  },
  {
    id: 'security',
    label: 'Security',
    items: [
      {
        id: 'authentication',
        category: 'security',
        type: 'auth',
        name: 'Authentication Service',
        technology: 'JWT / OAuth',
        description: 'Authenticates users and services.',
        color: '#dc2626',
        icon: KeyRound,
      },
      {
        id: 'authorization',
        category: 'security',
        type: 'authorization',
        name: 'Authorization Service',
        technology: 'Role-Based Access',
        description: 'Controls access to application resources.',
        color: '#e11d48',
        icon: ShieldCheck,
      },
    ],
  },
  {
    id: 'integration',
    label: 'External and Integration',
    items: [
      {
        id: 'external-api',
        category: 'integration',
        type: 'external-api',
        name: 'External API',
        technology: 'REST API',
        description: 'Third-party or external service.',
        color: '#9333ea',
        icon: ExternalLink,
      },
      {
        id: 'custom-component',
        category: 'custom',
        type: 'custom',
        name: 'Custom Component',
        technology: '',
        description: 'User-defined architecture component.',
        color: '#475569',
        icon: Braces,
      },
    ],
  },
]

export const connectionCategories = [
  {
    id: 'communication',
    label: 'Communication',
    items: [
      {
        id: 'rest-api',
        name: 'REST API',
        connectionType: 'api-call',
        protocol: 'HTTPS',
        description: 'Synchronous REST request.',
      },
      {
        id: 'graphql',
        name: 'GraphQL',
        connectionType: 'api-call',
        protocol: 'GraphQL',
        description: 'GraphQL query or mutation.',
      },
      {
        id: 'websocket',
        name: 'WebSocket',
        connectionType: 'bidirectional',
        protocol: 'WebSocket',
        description: 'Persistent bidirectional connection.',
      },
    ],
  },
  {
    id: 'data',
    label: 'Data Access',
    items: [
      {
        id: 'database-access',
        name: 'Database Access',
        connectionType: 'data-access',
        protocol: 'Database',
        description: 'Reads from or writes to a data store.',
      },
      {
        id: 'file-transfer',
        name: 'File Transfer',
        connectionType: 'file-transfer',
        protocol: 'HTTPS',
        description: 'Transfers files or stored objects.',
      },
    ],
  },
  {
    id: 'messaging',
    label: 'Messaging',
    items: [
      {
        id: 'message-queue',
        name: 'Message Queue',
        connectionType: 'message',
        protocol: 'Queue',
        description: 'Asynchronous queued message.',
      },
      {
        id: 'event-stream',
        name: 'Event Stream',
        connectionType: 'event',
        protocol: 'Event Stream',
        description: 'Publishes or consumes events.',
      },
    ],
  },
  {
    id: 'dependency',
    label: 'General',
    items: [
      {
        id: 'dependency',
        name: 'Dependency',
        connectionType: 'dependency',
        protocol: '',
        description: 'General architectural dependency.',
      },
    ],
  },
]

export function findComponentTemplate(templateId) {
  for (const category of componentCategories) {
    const template = category.items.find(
      (item) => item.id === templateId,
    )

    if (template) {
      return template
    }
  }

  return null
}

export function findConnectionTemplate(templateId) {
  for (const category of connectionCategories) {
    const template = category.items.find(
      (item) => item.id === templateId,
    )

    if (template) {
      return template
    }
  }

  return null
}
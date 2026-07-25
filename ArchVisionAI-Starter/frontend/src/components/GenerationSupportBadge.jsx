import {
  AlertCircle,
  CheckCircle2,
  CircleHelp,
  Clock3,
  Settings2,
} from 'lucide-react'


const UNKNOWN_SUPPORT = {
  supported: false,
  phase: "modeling-only",
  label: "Modeling Only",
  reason: (
    'The backend did not report generation support '
    + 'for this item.'
  ),
  generators: [],
  technologies: [],
  generated_files: [],
}


const PHASE_STYLES = {
  implemented: {
    icon: CheckCircle2,
    className: (
      'border-emerald-500/40 '
      + 'bg-emerald-500/10 '
      + 'text-emerald-300'
    ),
  },

  configured: {
    icon: Settings2,
    className: (
      'border-sky-500/40 '
      + 'bg-sky-500/10 '
      + 'text-sky-300'
    ),
  },

  represented: {
    icon: Clock3,
    className: (
      'border-amber-500/40 '
      + 'bg-amber-500/10 '
      + 'text-amber-300'
    ),
  },

  experimental: {
    icon: AlertCircle,
    className: (
      'border-violet-500/40 '
      + 'bg-violet-500/10 '
      + 'text-violet-300'
    ),
  },

  'modeling-only': {
    icon: AlertCircle,
    className: (
      'border-slate-500/40 '
      + 'bg-slate-500/10 '
      + 'text-slate-300'
    ),
  },

  unknown: {
    icon: CircleHelp,
    className: (
      'border-slate-600/50 '
      + 'bg-slate-800/70 '
      + 'text-slate-400'
    ),
  },
}


function normalizeSupport(
  support,
  isLoading,
) {
  if (isLoading) {
    return {
      ...UNKNOWN_SUPPORT,
      label: 'Checking Support',
      reason: (
        'Generation support is being loaded '
        + 'from the backend.'
      ),
    }
  }

  if (!support) {
    return UNKNOWN_SUPPORT
  }

  return {
    ...UNKNOWN_SUPPORT,
    ...support,
  }
}


export default function GenerationSupportBadge({
  support,
  isLoading = false,
  compact = false,
  showTooltip = true,
  className = '',
}) {
  const normalizedSupport = normalizeSupport(
    support,
    isLoading,
  )

  const phaseStyle = (
    PHASE_STYLES[
      normalizedSupport.phase
    ]
    || PHASE_STYLES["modeling-only"]
  )

  const Icon = phaseStyle.icon

  const badgeLabel = compact
    ? (
      normalizedSupport.supported
        ? 'Generation Supported'
        : normalizedSupport.phase === 'Modeling Only'
          ? 'Unknown'
          : 'Modeling Only'
    )
    : normalizedSupport.label

  const tooltip = showTooltip
    ? normalizedSupport.reason
    : undefined

  return (
    <span
      className={[
        'inline-flex',
        'items-center',
        'gap-1.5',
        'rounded-full',
        'border',
        'font-medium',
        'whitespace-nowrap',
        compact
          ? 'px-2 py-0.5 text-[10px]'
          : 'px-2.5 py-1 text-xs',
        phaseStyle.className,
        isLoading
          ? 'animate-pulse'
          : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      title={tooltip}
      aria-label={[
        badgeLabel,
        normalizedSupport.reason,
      ].join(': ')}
    >
      <Icon
        className={
          compact
            ? 'h-3 w-3'
            : 'h-3.5 w-3.5'
        }
        aria-hidden="true"
      />

      <span>
        {badgeLabel}
      </span>
    </span>
  )
}
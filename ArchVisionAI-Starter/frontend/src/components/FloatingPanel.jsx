import {
  ChevronDown,
  ChevronUp,
  GripHorizontal,
  X,
} from 'lucide-react'
import {
  useEffect,
  useRef,
  useState,
} from 'react'

let highestPanelZIndex = 60

function clamp(value, minimum, maximum) {
  return Math.min(
    Math.max(value, minimum),
    maximum,
  )
}

function getStartingPosition({
  parentWidth,
  parentHeight,
  panelWidth,
  panelHeight,
  placement,
  offset,
}) {
  const margin = 16

  switch (placement) {
    case 'top-right':
      return {
        x:
          parentWidth -
          panelWidth -
          margin -
          offset.x,
        y: margin + offset.y,
      }

    case 'bottom-left':
      return {
        x: margin + offset.x,
        y:
          parentHeight -
          panelHeight -
          margin -
          offset.y,
      }

    case 'bottom-right':
      return {
        x:
          parentWidth -
          panelWidth -
          margin -
          offset.x,
        y:
          parentHeight -
          panelHeight -
          margin -
          offset.y,
      }

    case 'center':
      return {
        x:
          (parentWidth - panelWidth) /
            2 +
          offset.x,
        y:
          (parentHeight - panelHeight) /
            2 +
          offset.y,
      }

    case 'top-left':
    default:
      return {
        x: margin + offset.x,
        y: margin + offset.y,
      }
  }
}

export default function FloatingPanel({
  title,
  subtitle = '',
  icon: Icon,
  children,
  footer = null,
  onClose,
  initialPlacement = 'top-left',
  initialOffset = { x: 0, y: 0 },
  initialSize = {
    width: 380,
    height: 560,
  },
  minimumSize = {
    width: 300,
    height: 220,
  },
  defaultMinimized = false,
  className = '',
}) {
  const panelRef = useRef(null)
  const dragStateRef = useRef(null)

  const [position, setPosition] =
    useState({
      x: 16,
      y: 16,
    })

  const [size, setSize] = useState(
    initialSize,
  )

  const [isMinimized, setIsMinimized] =
    useState(defaultMinimized)

  const [zIndex, setZIndex] =
    useState(() => {
      highestPanelZIndex += 1
      return highestPanelZIndex
    })

  const [isPositioned, setIsPositioned] =
    useState(false)

  function bringToFront() {
    highestPanelZIndex += 1
    setZIndex(highestPanelZIndex)
  }

  useEffect(() => {
    const panel = panelRef.current
    const parent = panel?.offsetParent

    if (!panel || !parent) {
      return
    }

    const parentBounds =
      parent.getBoundingClientRect()

    const nextPosition =
      getStartingPosition({
        parentWidth: parentBounds.width,
        parentHeight:
          parentBounds.height,
        panelWidth: initialSize.width,
        panelHeight: initialSize.height,
        placement: initialPlacement,
        offset: initialOffset,
      })

    setPosition({
      x: Math.max(8, nextPosition.x),
      y: Math.max(8, nextPosition.y),
    })

    setIsPositioned(true)
  }, [
    initialPlacement,
    initialOffset.x,
    initialOffset.y,
    initialSize.height,
    initialSize.width,
  ])

  useEffect(() => {
    function keepPanelInsideParent() {
      const panel = panelRef.current
      const parent = panel?.offsetParent

      if (!panel || !parent) {
        return
      }

      const parentBounds =
        parent.getBoundingClientRect()

      const panelBounds =
        panel.getBoundingClientRect()

      setPosition((current) => ({
        x: clamp(
          current.x,
          8,
          Math.max(
            8,
            parentBounds.width -
              panelBounds.width -
              8,
          ),
        ),
        y: clamp(
          current.y,
          8,
          Math.max(
            8,
            parentBounds.height -
              panelBounds.height -
              8,
          ),
        ),
      }))
    }

    window.addEventListener(
      'resize',
      keepPanelInsideParent,
    )

    return () => {
      window.removeEventListener(
        'resize',
        keepPanelInsideParent,
      )
    }
  }, [])

  function handleDragStart(event) {
    if (
      event.button !== 0 ||
      event.target.closest(
        '[data-panel-control="true"]',
      )
    ) {
      return
    }

    const panel = panelRef.current

    if (!panel) {
      return
    }

    bringToFront()

    dragStateRef.current = {
      pointerId: event.pointerId,
      startPointerX: event.clientX,
      startPointerY: event.clientY,
      startPanelX: position.x,
      startPanelY: position.y,
    }

    event.currentTarget.setPointerCapture(
      event.pointerId,
    )
  }

  function handleDragMove(event) {
    const dragState =
      dragStateRef.current

    if (
      !dragState ||
      dragState.pointerId !==
        event.pointerId
    ) {
      return
    }

    const panel = panelRef.current
    const parent = panel?.offsetParent

    if (!panel || !parent) {
      return
    }

    const parentBounds =
      parent.getBoundingClientRect()

    const panelBounds =
      panel.getBoundingClientRect()

    const nextX =
      dragState.startPanelX +
      event.clientX -
      dragState.startPointerX

    const nextY =
      dragState.startPanelY +
      event.clientY -
      dragState.startPointerY

    setPosition({
      x: clamp(
        nextX,
        8,
        Math.max(
          8,
          parentBounds.width -
            panelBounds.width -
            8,
        ),
      ),
      y: clamp(
        nextY,
        8,
        Math.max(
          8,
          parentBounds.height -
            panelBounds.height -
            8,
        ),
      ),
    })
  }

  function handleDragEnd(event) {
    if (
      dragStateRef.current
        ?.pointerId === event.pointerId
    ) {
      dragStateRef.current = null

      if (
        event.currentTarget.hasPointerCapture(
          event.pointerId,
        )
      ) {
        event.currentTarget.releasePointerCapture(
          event.pointerId,
        )
      }
    }
  }

  function handleResize(event) {
    const panel = panelRef.current
    const parent = panel?.offsetParent

    if (!panel || !parent) {
      return
    }

    const parentBounds =
      parent.getBoundingClientRect()

    const rect =
      panel.getBoundingClientRect()

    setSize({
      width: clamp(
        rect.width,
        minimumSize.width,
        Math.max(
          minimumSize.width,
          parentBounds.width -
            position.x -
            8,
        ),
      ),
      height: clamp(
        rect.height,
        minimumSize.height,
        Math.max(
          minimumSize.height,
          parentBounds.height -
            position.y -
            8,
        ),
      ),
    })
  }

  useEffect(() => {
    const panel = panelRef.current

    if (
      !panel ||
      typeof ResizeObserver ===
        'undefined'
    ) {
      return undefined
    }

    const observer =
      new ResizeObserver(() => {
        if (!isMinimized) {
          handleResize()
        }
      })

    observer.observe(panel)

    return () => observer.disconnect()
  }, [
    isMinimized,
    minimumSize.height,
    minimumSize.width,
    position.x,
    position.y,
  ])

  return (
    <section
      ref={panelRef}
      onPointerDown={bringToFront}
      className={[
        'absolute flex flex-col overflow-hidden rounded-xl border border-slate-700 bg-slate-950 text-white shadow-2xl',
        className,
      ].join(' ')}
      style={{
        left: position.x,
        top: position.y,
        width: size.width,
        height: isMinimized
          ? 'auto'
          : size.height,
        minWidth: minimumSize.width,
        minHeight: isMinimized
          ? undefined
          : minimumSize.height,
        maxWidth:
          'calc(100% - 16px)',
        maxHeight:
          'calc(100% - 16px)',
        resize: isMinimized
          ? 'none'
          : 'both',
        zIndex,
        visibility: isPositioned
          ? 'visible'
          : 'hidden',
      }}
    >
      <header
        onPointerDown={handleDragStart}
        onPointerMove={handleDragMove}
        onPointerUp={handleDragEnd}
        onPointerCancel={handleDragEnd}
        className="flex shrink-0 cursor-move touch-none items-start justify-between gap-3 border-b border-slate-800 bg-slate-950 px-4 py-3 select-none"
      >
        <div className="flex min-w-0 items-start gap-3">
          <span className="mt-0.5 text-slate-500">
            <GripHorizontal size={17} />
          </span>

          {Icon && (
            <span className="mt-0.5 text-indigo-300">
              <Icon size={17} />
            </span>
          )}

          <div className="min-w-0">
            <h2 className="truncate text-sm font-semibold">
              {title}
            </h2>

            {subtitle && (
              <p className="mt-1 truncate text-xs text-slate-400">
                {subtitle}
              </p>
            )}
          </div>
        </div>

        <div
          className="flex shrink-0 items-center gap-1"
          data-panel-control="true"
        >
          <button
            type="button"
            data-panel-control="true"
            onClick={() =>
              setIsMinimized(
                (current) => !current,
              )
            }
            className="rounded-md p-1.5 text-slate-400 transition hover:bg-slate-800 hover:text-white"
            aria-label={
              isMinimized
                ? 'Restore window'
                : 'Minimize window'
            }
            title={
              isMinimized
                ? 'Restore'
                : 'Minimize'
            }
          >
            {isMinimized ? (
              <ChevronDown size={16} />
            ) : (
              <ChevronUp size={16} />
            )}
          </button>

          {onClose && (
            <button
              type="button"
              data-panel-control="true"
              onClick={onClose}
              className="rounded-md p-1.5 text-slate-400 transition hover:bg-slate-800 hover:text-white"
              aria-label="Close window"
              title="Close"
            >
              <X size={16} />
            </button>
          )}
        </div>
      </header>

      {!isMinimized && (
        <>
          <div className="min-h-0 flex-1 overflow-y-auto">
            {children}
          </div>

          {footer && (
            <footer className="shrink-0 border-t border-slate-800 p-4">
              {footer}
            </footer>
          )}
        </>
      )}
    </section>
  )
}
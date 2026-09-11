interface BusynessIndicatorProps {
  level: string
}

export function BusynessIndicator({ level }: BusynessIndicatorProps) {
  const normalizedLevel = level.toLowerCase()
  return (
    <span className={`busyness-pill ${normalizedLevel}`}>
      <span className="busyness-dot" aria-hidden="true" />
      {normalizedLevel}
    </span>
  )
}

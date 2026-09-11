import { useEffect, useState } from 'react'
import { getClinicStats } from '../api'

interface StatsPanelProps {
  clinicId: number
}

export function StatsPanel({ clinicId }: StatsPanelProps) {
  const [observations, setObservations] = useState(0)
  const [error, setError] = useState('')

  useEffect(() => {
    let isCurrent = true
    setError('')
    getClinicStats(clinicId)
      .then((result) => {
        if (isCurrent) setObservations(result.hourly_stats.reduce((total, stat) => total + stat.sample_count, 0))
      })
      .catch((reason) => {
        if (isCurrent) setError(reason instanceof Error ? reason.message : 'Unable to load statistics')
      })
    return () => {
      isCurrent = false
    }
  }, [clinicId])

  return (
    <section className="p1-panel" aria-labelledby="stats-title">
      <p className="eyebrow">Model health</p>
      <h2 id="stats-title">Prediction statistics</h2>
      {error && <p className="form-error" role="alert">{error}</p>}
      <div className="stats-grid">
        <div className="stat-value"><strong>{observations.toLocaleString()}</strong><span>Total observations</span></div>
        <div className="stat-value"><strong>—</strong><span>MAE <small>Phase G</small></span></div>
        <div className="stat-value"><strong>—</strong><span>80% coverage <small>Phase G</small></span></div>
      </div>
    </section>
  )
}
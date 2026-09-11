import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { getClinicStats, type HourlyStat } from '../api'

interface HistoricalChartProps {
  clinicId: number
}

export function HistoricalChart({ clinicId }: HistoricalChartProps) {
  const [stats, setStats] = useState<HourlyStat[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    let isCurrent = true
    setError('')
    getClinicStats(clinicId)
      .then((result) => {
        if (isCurrent) setStats(result.hourly_stats)
      })
      .catch((reason) => {
        if (isCurrent) setError(reason instanceof Error ? reason.message : 'Unable to load history')
      })
    return () => {
      isCurrent = false
    }
  }, [clinicId])

  return (
    <section className="p1-panel" aria-labelledby="history-title">
      <div className="p1-panel-heading">
        <div>
          <p className="eyebrow">Historical patterns</p>
          <h2 id="history-title">Average wait by hour</h2>
        </div>
      </div>
      {error ? (
        <p className="form-error" role="alert">{error}</p>
      ) : (
        <div className="chart-frame">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats} margin={{ top: 8, right: 8, left: -16, bottom: 8 }}>
              <CartesianGrid stroke="#d9e1dc" vertical={false} />
              <XAxis dataKey="hour" tickFormatter={(hour) => `${hour}:00`} />
              <YAxis unit=" min" />
              <Tooltip formatter={(value) => [`${Number(value).toFixed(1)} min`, 'Average wait']} />
              <Bar dataKey="avg_wait" fill="#0d7770" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  )
}
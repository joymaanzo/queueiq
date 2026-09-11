import { useEffect, useState } from 'react'
import { getClinicForecast, type ForecastEntry } from '../api'
import { BusynessIndicator } from './BusynessIndicator'

interface StaffDashboardProps {
  clinicId: number
}

export function StaffDashboard({ clinicId }: StaffDashboardProps) {
  const [forecast, setForecast] = useState<ForecastEntry[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    let isCurrent = true
    setError('')
    getClinicForecast(clinicId)
      .then((result) => {
        if (isCurrent) setForecast(result.forecast)
      })
      .catch((reason) => {
        if (isCurrent) setError(reason instanceof Error ? reason.message : 'Unable to load forecast')
      })
    return () => {
      isCurrent = false
    }
  }, [clinicId])

  return (
    <section className="p1-panel" aria-labelledby="staff-title">
      <p className="eyebrow">Forward view</p>
      <h2 id="staff-title">Expected demand</h2>
      {error ? (
        <p className="form-error" role="alert">{error}</p>
      ) : (
        <div className="table-wrap">
          <table className="forecast-table">
            <thead>
              <tr><th>Window</th><th>Expected arrivals</th><th>Busyness</th></tr>
            </thead>
            <tbody>
              {forecast.map((entry) => (
                <tr key={entry.hours_ahead}>
                  <td>{entry.window}</td>
                  <td>{entry.expected_arrivals.toFixed(1)}</td>
                  <td><BusynessIndicator level={entry.busyness} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
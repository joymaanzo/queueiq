import { useState } from 'react'
import { predictWait, type Clinic, type PredictResponse } from '../api'
import { QueueSizeInput } from './QueueSizeInput'
import { TimeInput } from './TimeInput'

interface PredictionFormProps {
  clinic: Clinic | null
  onPredict: (prediction: PredictResponse) => void
}

function localDateTimeValue() {
  const date = new Date()
  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 16)
}

export function PredictionForm({ clinic, onPredict }: PredictionFormProps) {
  const [timestamp, setTimestamp] = useState(localDateTimeValue)
  const [queueLength, setQueueLength] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!clinic) return
    setIsLoading(true)
    setError('')
    try {
      const result = await predictWait({
        clinic_id: clinic.clinic_id,
        timestamp: new Date(timestamp).toISOString(),
        ...(queueLength === '' ? {} : { current_queue_length: Number(queueLength) }),
      })
      onPredict(result)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to get a prediction')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form className="prediction-form" onSubmit={submit}>
      <div className="form-grid">
        <TimeInput value={timestamp} onChange={setTimestamp} />
        <QueueSizeInput value={queueLength} onChange={setQueueLength} />
      </div>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="predict-button" type="submit" disabled={!clinic || isLoading}>
        {isLoading ? 'Calculating...' : 'Predict wait time'}
        <span aria-hidden="true">→</span>
      </button>
    </form>
  )
}

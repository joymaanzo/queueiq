import { useState } from 'react'
import { recordActualWait, type ApiRequestError } from '../api'

interface ActualWaitFormProps {
  predictionId: number
  onSubmitted: () => void
}

export function ActualWaitForm({ predictionId, onSubmitted }: ActualWaitFormProps) {
  const [actualWait, setActualWait] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setMessage('')
    setError('')
    setIsSubmitting(true)
    try {
      await recordActualWait({
        prediction_id: predictionId,
        actual_wait_minutes: Number(actualWait),
      })
      setActualWait('')
      setMessage('Thanks, recorded.')
      onSubmitted()
    } catch (reason) {
      const requestError = reason as ApiRequestError
      if (requestError.status === 409) {
        setError('You already reported a wait for this prediction.')
      } else {
        setError(reason instanceof Error ? reason.message : 'Unable to record actual wait')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form className="actual-wait-form" onSubmit={submit}>
      <div className="p1-form-heading">
        <div>
          <p className="eyebrow">Close the loop</p>
          <h3>How long did you wait?</h3>
        </div>
        <span className="mode-label">Prediction #{predictionId}</span>
      </div>
      <label className="field-label" htmlFor="actual-wait">
        Actual wait <span className="optional-label">minutes</span>
        <input
          className="field-control"
          id="actual-wait"
          type="number"
          min="0"
          max="600"
          step="1"
          value={actualWait}
          onChange={(event) => setActualWait(event.target.value)}
          required
        />
      </label>
      {message && <p className="form-success" role="status">{message}</p>}
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="secondary-button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Recording...' : 'Record actual wait'}
      </button>
    </form>
  )
}
import type { PredictResponse } from '../api'
import { BusynessIndicator } from './BusynessIndicator'

interface PredictionCardProps {
  prediction: PredictResponse
}

export function PredictionCard({ prediction }: PredictionCardProps) {
  return (
    <section className="prediction-card" aria-live="polite">
      <div className="prediction-card-topline">
        <span className="eyebrow">Your estimate</span>
        <span className="mode-label">{prediction.mode} mode</span>
      </div>
      <div className="wait-number">
        {Math.round(prediction.predicted_wait_minutes)}
        <span>minutes</span>
      </div>
      <div className="range-row">
        <span>Likely range</span>
        <strong>
          {Math.round(prediction.confidence_interval_lower)}–{Math.round(prediction.confidence_interval_upper)} min
        </strong>
      </div>
      <p className="interval-note">80% prediction interval</p>
      <div className="prediction-footer">
        <span>Current conditions</span>
        <BusynessIndicator level={prediction.busyness} />
      </div>
    </section>
  )
}

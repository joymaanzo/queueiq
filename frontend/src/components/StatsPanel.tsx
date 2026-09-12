import { useEffect, useState } from 'react'
import { getEvaluation, type EvaluationResponse } from '../api'

interface StatsPanelProps {
  clinicId: number
}

export function StatsPanel({ clinicId }: StatsPanelProps) {
  const [evaluation, setEvaluation] = useState<EvaluationResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let isCurrent = true
    setError('')
    getEvaluation(clinicId)
      .then((result) => {
        if (isCurrent) setEvaluation(result)
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
      {evaluation && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="border border-[#d9e1dc] bg-[#fffef9] p-6">
            <strong className="mb-2 block text-3xl tracking-[-0.05em]">{evaluation.predictions_with_actuals.toLocaleString()}</strong>
            <span className="font-mono text-[11px] uppercase text-[#718187]">Predictions with actuals</span>
          </div>
          <div className="border border-[#d9e1dc] bg-[#fffef9] p-6">
            <strong className="mb-2 block text-3xl tracking-[-0.05em]">{evaluation.events_evaluated.toLocaleString()}</strong>
            <span className="font-mono text-[11px] uppercase text-[#718187]">Events evaluated</span>
          </div>
          <div className="border border-[#d9e1dc] bg-[#fffef9] p-6">
            <strong className="mb-2 block text-3xl tracking-[-0.05em]">{evaluation.model_mae.toFixed(1)} min</strong>
            <span className="font-mono text-[11px] uppercase text-[#718187]">Model MAE</span>
          </div>
          <div className="border border-[#d9e1dc] bg-[#fffef9] p-6">
            <strong className="mb-2 block text-3xl tracking-[-0.05em]">{evaluation.baseline_mae.toFixed(1)} min</strong>
            <span className="font-mono text-[11px] uppercase text-[#718187]">Baseline MAE</span>
          </div>
          <div className="border border-[#d9e1dc] bg-[#fffef9] p-6">
            <strong className="mb-2 block text-3xl tracking-[-0.05em]">{evaluation.improvement_pct.toFixed(1)}%</strong>
            <span className="font-mono text-[11px] uppercase text-[#718187]">Improvement over baseline</span>
          </div>
          <div className="border border-[#d9e1dc] bg-[#fffef9] p-6">
            <strong className="mb-2 block text-3xl tracking-[-0.05em]">{(evaluation.interval_coverage * 100).toFixed(1)}%</strong>
            <span className="font-mono text-[11px] uppercase text-[#718187]">Interval coverage</span>
          </div>
        </div>
      )}
    </section>
  )
}
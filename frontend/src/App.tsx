import { useCallback, useState } from 'react'
import type { Clinic, PredictResponse } from './api'
import { ClinicSelector } from './components/ClinicSelector'
import { PredictionCard } from './components/PredictionCard'
import { PredictionForm } from './components/PredictionForm'
import './App.css'

function App() {
  const [selectedClinic, setSelectedClinic] = useState<Clinic | null>(null)
  const [prediction, setPrediction] = useState<PredictResponse | null>(null)

  const handleClinicChange = useCallback((clinic: Clinic) => {
    setSelectedClinic(clinic)
    setPrediction(null)
  }, [])

  return (
    <main className="app-shell">
      <header className="app-header">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">Q</div>
          <div>
            <span className="brand-name">QueueIQ</span>
            <span className="brand-caption">Patient flow intelligence</span>
          </div>
        </div>
        <span className="status-chip"><span /> Synthetic data · live model</span>
      </header>

      <section className="hero-copy">
        <p className="kicker">Know before you go</p>
        <h1>Clinic wait-time<br /><em>made clearer.</em></h1>
        <p className="hero-description">
          Select a clinic and arrival time to see an evidence-based estimate for the minutes ahead.
        </p>
      </section>

      <section className="workspace-grid">
        <div className="control-panel">
          <div className="section-heading">
            <span className="step-number">01</span>
            <div>
              <h2>Set your visit</h2>
              <p>Tell us where and when you are going.</p>
            </div>
          </div>
          <ClinicSelector selectedClinic={selectedClinic} onChange={handleClinicChange} />
          <PredictionForm clinic={selectedClinic} onPredict={setPrediction} />
        </div>

        <div className="result-panel">
          {prediction ? (
            <PredictionCard prediction={prediction} />
          ) : (
            <div className="empty-result">
              <div className="pulse-ring" aria-hidden="true"><span>↗</span></div>
              <p className="eyebrow">Prediction ready when you are</p>
              <h2>Your wait estimate<br />will appear here.</h2>
              <p>Choose a clinic and time, then run the model.</p>
            </div>
          )}
        </div>
      </section>

      <footer className="app-footer">
        <span>QueueIQ / Module 2</span>
        <span>Built for calmer arrivals</span>
      </footer>
    </main>
  )
}

export default App

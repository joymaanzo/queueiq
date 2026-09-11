import { useCallback, useState } from 'react'
import type { Clinic, PredictResponse } from './api'
import { ActualWaitForm } from './components/ActualWaitForm'
import { ClinicSelector } from './components/ClinicSelector'
import { HistoricalChart } from './components/HistoricalChart'
import { PredictionCard } from './components/PredictionCard'
import { PredictionForm } from './components/PredictionForm'
import { StaffDashboard } from './components/StaffDashboard'
import { StatsPanel } from './components/StatsPanel'
import './App.css'

type Tab = 'predict' | 'history' | 'staff' | 'stats'

function App() {
  const [selectedClinic, setSelectedClinic] = useState<Clinic | null>(null)
  const [prediction, setPrediction] = useState<PredictResponse | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>('predict')

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

      <nav className="tab-nav flex gap-1 border-b border-[#d9e1dc]" aria-label="QueueIQ views">
        {(['predict', 'history', 'staff', 'stats'] as const).map((tab) => (
          <button
            className={`px-4 py-3 text-xs font-extrabold uppercase tracking-[0.08em] transition-colors ${activeTab === tab ? 'border-b-2 border-[#0d7770] text-[#075c59]' : 'text-[#718187] hover:text-[#112b35]'}`}
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
          >
            {tab[0].toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </nav>

      <section className="hero-copy">
        <p className="kicker">Know before you go</p>
        <h1>Clinic wait-time<br /><em>made clearer.</em></h1>
        <p className="hero-description">
          Select a clinic and arrival time to see an evidence-based estimate for the minutes ahead.
        </p>
      </section>

      {activeTab === 'predict' && (
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
              <div className="prediction-stack">
                <PredictionCard prediction={prediction} />
                <ActualWaitForm predictionId={prediction.prediction_id} onSubmitted={() => undefined} />
              </div>
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
      )}

      {activeTab !== 'predict' && (
        <section className="p1-view">
          {selectedClinic ? (
            activeTab === 'history' ? <HistoricalChart clinicId={selectedClinic.clinic_id} />
              : activeTab === 'staff' ? <StaffDashboard clinicId={selectedClinic.clinic_id} />
                : <StatsPanel clinicId={selectedClinic.clinic_id} />
          ) : (
            <div className="p1-panel empty-view">
              <p className="eyebrow">Choose a clinic first</p>
              <h2>Clinic data will appear here.</h2>
              <button className="secondary-button" type="button" onClick={() => setActiveTab('predict')}>
                Go to Predict
              </button>
            </div>
          )}
        </section>
      )}

      <footer className="app-footer">
        <span>QueueIQ / Module 2</span>
        <span>Built for calmer arrivals</span>
      </footer>
    </main>
  )
}

export default App

import { useEffect, useState } from 'react'
import { listClinics, type Clinic } from '../api'

interface ClinicSelectorProps {
  selectedClinic: Clinic | null
  onChange: (clinic: Clinic) => void
}

export function ClinicSelector({ selectedClinic, onChange }: ClinicSelectorProps) {
  const [clinics, setClinics] = useState<Clinic[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    listClinics()
      .then((items) => {
        setClinics(items)
        if (!selectedClinic && items[0]) onChange(items[0])
      })
      .catch((reason: Error) => setError(reason.message))
  }, [onChange, selectedClinic])

  return (
    <label className="field-label">
      Clinic
      <select
        className="field-control"
        value={selectedClinic?.clinic_id ?? ''}
        onChange={(event) => {
          const clinic = clinics.find((item) => item.clinic_id === Number(event.target.value))
          if (clinic) onChange(clinic)
        }}
        disabled={clinics.length === 0}
      >
        <option value="">{error || 'Loading clinics...'}</option>
        {clinics.map((clinic) => (
          <option key={clinic.clinic_id} value={clinic.clinic_id}>
            {clinic.name} · {clinic.location}
          </option>
        ))}
      </select>
      {selectedClinic && (
        <span className="field-hint">
          {selectedClinic.service_type} · {selectedClinic.hours_open} · {selectedClinic.days_open}
        </span>
      )}
    </label>
  )
}

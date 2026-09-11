interface QueueSizeInputProps {
  value: string
  onChange: (value: string) => void
}

export function QueueSizeInput({ value, onChange }: QueueSizeInputProps) {
  return (
    <label className="field-label">
      Current queue length (optional)
      <input
        className="field-control"
        type="number"
        min="0"
        max="100"
        placeholder="e.g. 5"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
      <span className="field-hint">
        Leave blank for a typical wait. If you can see the line right now, enter how many people are ahead of you for a sharper estimate.
      </span>
    </label>
  )
}

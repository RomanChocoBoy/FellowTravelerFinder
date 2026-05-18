import { useState, useEffect } from 'react'
import { api, formatDate } from '../../api/client'
import { useAuth } from '../../context/AuthContext'

export default function ComplaintForm() {
  const { user } = useAuth()
  const [contacts, setContacts] = useState([])
  const [selected, setSelected] = useState('')
  const [reason, setReason] = useState('')
  const [description, setDescription] = useState('')
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.tripContacts(user.id).then(setContacts).catch((e) => setError(e.message))
  }, [user.id])

  const submit = async (e) => {
    e.preventDefault()
    if (!selected) return
    const [tripId, recipientId] = selected.split(':').map(Number)
    setError('')
    setMsg('')
    try {
      await api.createComplaint({
        sender_id: user.id,
        recipient_id: recipientId,
        trip_id: tripId,
        reason,
        description,
      })
      setMsg('Жалоба отправлена')
      setReason('')
      setDescription('')
      setSelected('')
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="card">
      <h3>Подать жалобу</h3>
      <p style={{ fontSize: 13, color: '#6b7280' }}>
        Жалобу можно подать только на участника общей с вами поездки.
      </p>
      {contacts.length === 0 && (
        <p style={{ color: '#6b7280' }}>Нет доступных пользователей. Нужна активная бронь на поездку.</p>
      )}
      <form onSubmit={submit}>
        <label>
          На кого (поездка)
          <select value={selected} onChange={(e) => setSelected(e.target.value)} required>
            <option value="">Выберите...</option>
            {contacts.map((c) => (
              <option key={`${c.trip_id}-${c.user_id}`} value={`${c.trip_id}:${c.user_id}`}>
                {c.user_name} — {c.from_place} → {c.to_place} ({formatDate(c.date)})
              </option>
            ))}
          </select>
        </label>
        <label>
          Причина
          <input value={reason} onChange={(e) => setReason(e.target.value)} required />
        </label>
        <label>
          Описание
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
        </label>
        {error && <p className="error">{error}</p>}
        {msg && <p className="success">{msg}</p>}
        <button type="submit" disabled={contacts.length === 0}>
          Отправить жалобу
        </button>
      </form>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { api, formatDate } from '../../api/client'
import { useAuth } from '../../context/AuthContext'

export default function MyTrips({ refreshKey }) {
  const { user } = useAuth()
  const [trips, setTrips] = useState([])
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  const load = () => {
    api.myTrips(user.id).then(setTrips)
  }

  useEffect(() => {
    load()
  }, [user.id, refreshKey])

  const remove = async (tripId) => {
    if (!window.confirm('Удалить поездку? Все заявки будут отменены.')) return
    setError('')
    try {
      await api.deleteTrip(tripId, user.id)
      setMsg('Поездка удалена')
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  const statusLabel = { active: 'Активна', cancelled: 'Отменена' }

  return (
    <div className="card">
      <h3>Мои поездки</h3>
      {error && <p className="error">{error}</p>}
      {msg && <p className="success">{msg}</p>}
      {trips.length === 0 && <p style={{ color: '#6b7280' }}>Нет опубликованных поездок</p>}
      {trips.map((t) => (
        <div key={t.id} className="trip-card">
          <div>
            <div className="trip-card-route">
              {t.from_place} → {t.to_place}
            </div>
            <div className="trip-card-meta">
              {formatDate(t.date)} · {t.price} ₽ · свободно мест: {t.available_seats}
              <br />
              <span className={`badge ${t.status === 'active' ? 'badge-green' : 'badge-gray'}`}>
                {statusLabel[t.status] || t.status}
              </span>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            {t.status === 'active' && (
              <button type="button" className="danger" onClick={() => remove(t.id)}>
                Удалить
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

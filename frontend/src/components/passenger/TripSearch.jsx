import { useState } from 'react'
import { api, formatDate } from '../../api/client'
import { useAuth } from '../../context/AuthContext'

export default function TripSearch() {
  const { user } = useAuth()
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [trips, setTrips] = useState([])
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  const search = async (e) => {
    e.preventDefault()
    setError('')
    setMsg('')
    try {
      const list = await api.searchTrips(from, to)
      setTrips(list)
      if (list.length === 0) {
        setMsg('Поездок не найдено. Попробуйте другие города.')
      }
    } catch (e) {
      setError(e.message)
    }
  }

  const book = async (tripId) => {
    setMsg('')
    try {
      await api.createBooking({ trip_id: tripId, passenger_id: user.id })
      setMsg('Заявка отправлена водителю. Статус — в разделе «Бронирования».')
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="card">
      <h3>Поиск поездки</h3>
      <p style={{ fontSize: 13, color: '#6b7280', marginBottom: 16 }}>
        Укажите города — дату и время выберите из найденных вариантов.
      </p>
      <form onSubmit={search}>
        <div className="form-row">
          <label>
            Откуда
            <input value={from} onChange={(e) => setFrom(e.target.value)} placeholder="Москва" required />
          </label>
          <label>
            Куда
            <input value={to} onChange={(e) => setTo(e.target.value)} placeholder="Санкт-Петербург" required />
          </label>
          <label style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button type="submit" style={{ width: '100%', marginTop: 22 }}>
              Найти
            </button>
          </label>
        </div>
      </form>
      {error && <p className="error">{error}</p>}
      {msg && <p className={trips.length ? 'success' : 'error'}>{msg}</p>}

      {trips.length > 0 && (
        <p style={{ marginTop: 20, fontWeight: 600 }}>Найдено {trips.length} поездок</p>
      )}

      {trips.map((t) => (
        <div key={t.id} className="trip-card">
          <div>
            <div className="trip-card-route">
              {t.from_place} → {t.to_place}
            </div>
            <div className="trip-card-meta">
              {formatDate(t.date)}
              <br />
              Мест: {t.available_seats}
            </div>
            <div className="trip-card-driver">
              Водитель: {t.driver_name} · рейтинг {t.driver_rating}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className="trip-card-price">{t.price} ₽</div>
            <button type="button" onClick={() => book(t.id)} style={{ marginTop: 12 }}>
              Забронировать
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

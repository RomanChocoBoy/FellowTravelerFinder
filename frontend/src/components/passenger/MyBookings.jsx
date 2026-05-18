import { useState, useEffect } from 'react'
import { api, formatDate } from '../../api/client'
import { useAuth } from '../../context/AuthContext'

const statusMap = {
  pending: { label: 'Ожидает подтверждения', class: 'badge-yellow' },
  approved: { label: 'Подтверждено', class: 'badge-green' },
  cancelled: { label: 'Отменено', class: 'badge-gray' },
}

export default function MyBookings() {
  const { user } = useAuth()
  const [bookings, setBookings] = useState([])
  const [error, setError] = useState('')

  const load = () => {
    api.bookings(user.id).then(setBookings).catch((e) => setError(e.message))
  }

  useEffect(() => {
    load()
  }, [user.id])

  const cancel = async (id) => {
    try {
      await api.cancelBooking(id)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="card">
      <h3>Мои бронирования</h3>
      {error && <p className="error">{error}</p>}
      {bookings.length === 0 && <p style={{ color: '#6b7280' }}>Пока нет бронирований</p>}
      {bookings.map((b) => {
        const st = statusMap[b.status] || { label: b.status, class: 'badge-gray' }
        return (
          <div key={b.id} className="booking-card">
            <div className="booking-card-header">
              <div className="booking-card-route">
                {b.from_place} → {b.to_place}
              </div>
              <span className={`badge ${st.class}`}>{st.label}</span>
            </div>
            <div className="booking-card-body">
              <span>
                <strong>Дата:</strong> {formatDate(b.trip_date)}
              </span>
              <span>
                <strong>Водитель:</strong> {b.driver_name}
              </span>
              <span>
                <strong>Стоимость:</strong>{' '}
                <span style={{ color: '#16a34a', fontWeight: 600 }}>{b.price} ₽</span>
              </span>
              <span>
                <strong>Забронировано:</strong> {formatDate(b.booking_date)}
              </span>
            </div>
            {(b.status === 'pending' || b.status === 'approved') && (
              <div className="booking-card-actions">
                <button type="button" className="danger" onClick={() => cancel(b.id)}>
                  Отменить
                </button>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

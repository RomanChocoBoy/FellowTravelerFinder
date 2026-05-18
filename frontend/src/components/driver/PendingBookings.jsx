import { useState, useEffect } from 'react'
import { api } from '../../api/client'
import { useAuth } from '../../context/AuthContext'

export default function PendingBookings({ refreshKey }) {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [error, setError] = useState('')

  const load = () => {
    api.pendingBookings(user.id).then(setItems).catch((e) => setError(e.message))
  }

  useEffect(() => {
    load()
  }, [user.id, refreshKey])

  const approve = async (id) => {
    try {
      await api.approveBooking(id)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="card">
      <h3>Заявки на бронирование</h3>
      {error && <p className="error">{error}</p>}
      {items.length === 0 && <p>Нет новых заявок</p>}
      {items.map((b) => (
        <div key={b.id} className="list-item">
          <strong>{b.passenger_name}</strong>: {b.from_place} → {b.to_place}
          <br />
          <button type="button" onClick={() => approve(b.id)}>
            Подтвердить
          </button>
        </div>
      ))}
    </div>
  )
}

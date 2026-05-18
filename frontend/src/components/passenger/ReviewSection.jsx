import { useState, useEffect } from 'react'
import { api } from '../../api/client'
import { useAuth } from '../../context/AuthContext'

export default function ReviewSection() {
  const { user } = useAuth()
  const [trips, setTrips] = useState([])
  const [tripId, setTripId] = useState('')
  const [rating, setRating] = useState(5)
  const [comment, setComment] = useState('')
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  useEffect(() => {
    api.reviewableTrips(user.id)
      .then((list) => {
        const seen = new Set()
        const unique = list.filter((t) => {
          if (seen.has(t.trip_id)) return false
          seen.add(t.trip_id)
          return true
        })
        setTrips(unique)
      })
      .catch((e) => setError(e.message))
  }, [user.id])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setMsg('')
    try {
      await api.createReview({
        trip_id: Number(tripId),
        author_id: user.id,
        rating: Number(rating),
        comment,
      })
      setMsg('Отзыв опубликован')
      setComment('')
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="card">
      <h3>Оставить отзыв</h3>
      <p style={{ fontSize: 14, color: '#666' }}>
        Отзыв можно оставить только по поездке с подтверждённым бронированием.
      </p>
      <form onSubmit={submit}>
        <label>
          Поездка
          <select value={tripId} onChange={(e) => setTripId(e.target.value)} required>
            <option value="">Выберите поездку</option>
            {trips.map((t, index) => (
              <option key={`trip-${t.trip_id}-${index}`} value={t.trip_id}>
                {t.from_place} → {t.to_place} ({t.date?.slice(0, 10)})
              </option>
            ))}
          </select>
        </label>
        <label>
          Оценка (1–5)
          <input
            type="number"
            min={1}
            max={5}
            value={rating}
            onChange={(e) => setRating(e.target.value)}
            required
          />
        </label>
        <label>
          Комментарий
          <textarea value={comment} onChange={(e) => setComment(e.target.value)} rows={3} />
        </label>
        {error && <p className="error">{error}</p>}
        {msg && <p className="success">{msg}</p>}
        <button type="submit">Опубликовать</button>
      </form>
    </div>
  )
}

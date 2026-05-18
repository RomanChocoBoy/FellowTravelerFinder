import { useState } from 'react'
import { api, todayInputValue } from '../../api/client'
import { useAuth } from '../../context/AuthContext'

export default function PublishTrip({ onPublished }) {
  const { user } = useAuth()
  const [form, setForm] = useState({
    from_place: '',
    to_place: '',
    date: '',
    time: '10:00',
    price: '',
    seats: '3',
  })
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setMsg('')
    if (form.date < todayInputValue()) {
      setError('Дата поездки не может быть раньше сегодняшнего дня')
      return
    }
    try {
      await api.publishTrip({
        driver_id: user.id,
        ...form,
        price: parseFloat(form.price),
        seats: parseInt(form.seats, 10),
      })
      setMsg('Поездка опубликована')
      setForm({ from_place: '', to_place: '', date: '', time: '10:00', price: '', seats: '3' })
      onPublished?.()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="card">
      <h3>Публикация поездки</h3>
      <form onSubmit={submit}>
        <label>
          Пункт отправления
          <input value={form.from_place} onChange={set('from_place')} placeholder="Воркута" required />
        </label>
        <label>
          Пункт назначения
          <input value={form.to_place} onChange={set('to_place')} placeholder="Новосибирск" required />
        </label>
        <div className="form-row" style={{ gridTemplateColumns: '1fr 1fr' }}>
          <label>
            Дата
            <input type="date" value={form.date} onChange={set('date')} min={todayInputValue()} required />
          </label>
          <label>
            Время
            <input type="time" value={form.time} onChange={set('time')} required />
          </label>
        </div>
        <div className="form-row" style={{ gridTemplateColumns: '1fr 1fr' }}>
          <label>
            Цена (₽)
            <input type="number" min={0} value={form.price} onChange={set('price')} required />
          </label>
          <label>
            Количество мест
            <input type="number" min={1} value={form.seats} onChange={set('seats')} required />
          </label>
        </div>
        {error && <p className="error">{error}</p>}
        {msg && <p className="success">{msg}</p>}
        <button type="submit">Опубликовать</button>
      </form>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { api, formatDate } from '../../api/client'

const statusRu = {
  pending: { label: 'На рассмотрении', class: 'badge-yellow' },
  approved: { label: 'Принята', class: 'badge-green' },
  rejected: { label: 'Отклонена', class: 'badge-red' },
}

export default function ComplaintsList() {
  const [complaints, setComplaints] = useState([])
  const [error, setError] = useState('')

  const load = () => {
    api.complaints().then(setComplaints).catch((e) => setError(e.message))
  }

  useEffect(() => {
    load()
  }, [])

  const approve = async (id) => {
    await api.approveComplaint(id)
    load()
  }

  const reject = async (id) => {
    await api.rejectComplaint(id)
    load()
  }

  return (
    <div className="card">
      <h3>Модерация жалоб</h3>
      {error && <p className="error">{error}</p>}
      {complaints.length === 0 && <p style={{ color: '#6b7280' }}>Жалоб нет</p>}
      {complaints.map((c) => {
        const st = statusRu[c.status] || { label: c.status, class: 'badge-gray' }
        return (
          <article key={c.id} className="complaint-card">
            <header className="complaint-card-header">
              <strong>Жалоба #{c.id}</strong>
              <span className={`badge ${st.class}`}>{st.label}</span>
            </header>

            <section className="complaint-card-grid">
              <section className="complaint-user-block">
                <strong>Отправитель</strong>
                {c.sender_name}
                <br />
                <span style={{ fontSize: 12, color: '#6b7280' }}>{c.sender_email}</span>
              </section>
              <section className="complaint-user-block">
                <strong>На кого</strong>
                {c.recipient_name}
                <br />
                <span style={{ fontSize: 12, color: '#6b7280' }}>{c.recipient_email}</span>
              </section>
            </section>

            <p className="complaint-reason">{c.reason}</p>
            {c.description && <p className="complaint-desc">{c.description}</p>}
            <p className="complaint-date">{formatDate(c.date)}</p>

            {c.status === 'pending' && (
              <footer className="complaint-actions">
                <button type="button" onClick={() => approve(c.id)}>
                  Принять
                </button>
                <button type="button" className="danger" onClick={() => reject(c.id)}>
                  Отклонить
                </button>
              </footer>
            )}
          </article>
        )
      })}
    </div>
  )
}

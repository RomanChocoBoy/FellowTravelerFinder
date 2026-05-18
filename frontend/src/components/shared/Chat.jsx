import { useState, useEffect } from 'react'
import { api, formatDate } from '../../api/client'
import { useAuth } from '../../context/AuthContext'

export default function Chat() {
  const { user } = useAuth()
  const [threads, setThreads] = useState([])
  const [active, setActive] = useState(null)
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [error, setError] = useState('')

  const loadThreads = () => {
    api.chatThreads(user.id).then(setThreads).catch((e) => setError(e.message))
  }

  useEffect(() => {
    loadThreads()
  }, [user.id])

  const openThread = async (thread) => {
    setActive(thread)
    setError('')
    try {
      const list = await api.messages(user.id, thread.user_id, thread.trip_id)
      setMessages(list)
    } catch (e) {
      setError(e.message)
    }
  }

  const send = async (e) => {
    e.preventDefault()
    if (!active || !text.trim()) return
    try {
      await api.sendMessage({
        trip_id: active.trip_id,
        sender_id: user.id,
        recipient_id: active.user_id,
        text: text.trim(),
      })
      setText('')
      const list = await api.messages(user.id, active.user_id, active.trip_id)
      setMessages(list)
      loadThreads()
    } catch (e) {
      setError(e.message)
    }
  }

  const threadKey = (t) => `${t.trip_id}-${t.user_id}`

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <h3 style={{ padding: '16px 20px 0', margin: 0 }}>Чат</h3>
      <p style={{ padding: '0 20px', fontSize: 13, color: '#6b7280' }}>
        Доступны только собеседники по вашим поездкам.
      </p>
      {error && <p className="error" style={{ padding: '0 20px' }}>{error}</p>}

      <div className="chat-layout" style={{ marginTop: 12 }}>
        <div className="chat-sidebar">
          {threads.length === 0 && (
            <div className="chat-empty">Нет чатов. Сначала забронируйте или подтвердите поездку.</div>
          )}
          {threads.map((t) => (
            <button
              key={threadKey(t)}
              type="button"
              className={`chat-thread ${active && threadKey(active) === threadKey(t) ? 'active' : ''}`}
              onClick={() => openThread(t)}
            >
              <div className="chat-thread-name">{t.user_name}</div>
              <div className="chat-thread-route">
                {t.from_place} → {t.to_place}, {formatDate(t.date)}
              </div>
              {t.last_message && <div className="chat-thread-preview">{t.last_message}</div>}
            </button>
          ))}
        </div>

        <div className="chat-main">
          {!active ? (
            <div className="chat-empty">Выберите диалог слева</div>
          ) : (
            <>
              <div className="chat-main-header">
                {active.user_name}
                <small>
                  {active.from_place} → {active.to_place}
                </small>
              </div>
              <div className="chat-messages">
                {messages.map((m) => (
                  <div
                    key={m.id}
                    className={`chat-bubble ${m.sender_id === user.id ? 'me' : 'them'}`}
                  >
                    {m.text}
                  </div>
                ))}
              </div>
              <form className="chat-input-row" onSubmit={send}>
                <input
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Введите сообщение..."
                />
                <button type="submit">Отправить</button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

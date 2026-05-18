import { useState, useEffect } from 'react'
import { api } from '../../api/client'

const roleRu = { passenger: 'Пассажир', reader: 'Водитель', admin: 'Админ' }

export default function UsersList() {
  const [users, setUsers] = useState([])
  const [error, setError] = useState('')

  const load = () => {
    api.allUsers().then(setUsers).catch((e) => setError(e.message))
  }

  useEffect(() => {
    load()
  }, [])

  const toggleBlock = async (u) => {
    try {
      if (u.status === 'blocked') {
        await api.unblockUser(u.id)
      } else {
        await api.blockUser(u.id)
      }
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="card">
      <h3>Управление пользователями</h3>
      {error && <p className="error">{error}</p>}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e5e7eb', textAlign: 'left' }}>
              <th style={{ padding: '10px 8px' }}>ID</th>
              <th style={{ padding: '10px 8px' }}>Имя</th>
              <th style={{ padding: '10px 8px' }}>Email</th>
              <th style={{ padding: '10px 8px' }}>Роль</th>
              <th style={{ padding: '10px 8px' }}>Рейтинг</th>
              <th style={{ padding: '10px 8px' }}>Статус</th>
              <th style={{ padding: '10px 8px' }}>Действия</th>
            </tr>
          </thead>
          <tbody>
            {users
              .filter((u) => u.role !== 'admin')
              .map((u) => (
                <tr key={u.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '12px 8px' }}>{u.id}</td>
                  <td style={{ padding: '12px 8px' }}>{u.name}</td>
                  <td style={{ padding: '12px 8px' }}>{u.email}</td>
                  <td style={{ padding: '12px 8px' }}>{roleRu[u.role]}</td>
                  <td style={{ padding: '12px 8px' }}>{u.rating}</td>
                  <td style={{ padding: '12px 8px' }}>
                    <span className={`badge ${u.status === 'blocked' ? 'badge-red' : 'badge-green'}`}>
                      {u.status === 'blocked' ? 'Заблокирован' : 'Активен'}
                    </span>
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    <button
                      type="button"
                      className={u.status === 'blocked' ? '' : 'danger'}
                      onClick={() => toggleBlock(u)}
                    >
                      {u.status === 'blocked' ? 'Разблокировать' : 'Заблокировать'}
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

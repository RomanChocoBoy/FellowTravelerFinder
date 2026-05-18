import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const roleLabels = {
  passenger: 'Пассажир',
  reader: 'Водитель',
  admin: 'Администратор',
}

export default function Header({ title }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="header">
      <div>
        <h1>{title}</h1>
        {user && (
          <small>
            {user.name} · {roleLabels[user.role] || user.role} · рейтинг {user.rating}
          </small>
        )}
      </div>
      <div>
        <button type="button" className="secondary" onClick={handleLogout}>
          Выйти
        </button>
      </div>
    </header>
  )
}

import { useNavigate } from 'react-router-dom'
import BrandLogo from './BrandLogo'
import { useAuth } from '../../context/AuthContext'

const roleLabels = {
  passenger: 'Пассажир',
  reader: 'Водитель',
  admin: 'Администратор',
}

export default function MobileShell({ tabs, activeTab, onTabChange, children, wide = false }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className={`app-shell ${wide ? 'app-shell--wide' : ''}`}>
      <header className="top-bar">
        <BrandLogo size="sm" />
        <div className="top-bar__actions">
          {user && (
            <span className="top-bar__user" title={user.email}>
              {user.name}
            </span>
          )}
          <button type="button" className="btn-text" onClick={handleLogout}>
            Выйти
          </button>
        </div>
      </header>

      {user && (
        <p className="page-subtitle">
          {roleLabels[user.role]} · рейтинг {user.rating}
        </p>
      )}

      <nav className="tabs--desktop" aria-label="Разделы">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            className={activeTab === t.id ? 'active' : 'secondary'}
            onClick={() => onTabChange(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main className="main-content">{children}</main>

      <nav className="bottom-nav" aria-label="Меню">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            className={activeTab === t.id ? 'active' : ''}
            onClick={() => onTabChange(t.id)}
          >
            <span className="bottom-nav__label">{t.short || t.label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}

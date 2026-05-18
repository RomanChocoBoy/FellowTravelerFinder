import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import BrandLogo from '../components/layout/BrandLogo'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const user = await api.login({ email, password })
      login(user)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="auth-page">
      <BrandLogo size="lg" centered showTagline />
      <div className="card auth-card">
        <h2>Вход</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Email
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
          </label>
          <label>
            Пароль
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </label>
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn-block">
            Войти
          </button>
        </form>
        <p className="auth-footer">
          Нет аккаунта? <Link to="/register">Регистрация</Link>
        </p>
      </div>
    </div>
  )
}

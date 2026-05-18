import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import BrandLogo from '../components/layout/BrandLogo'

export default function RegisterPage() {
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    role: 'passenger',
  })
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const user = await api.register(form)
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
        <h2>Регистрация</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Имя
            <input value={form.name} onChange={set('name')} required autoComplete="name" />
          </label>
          <label>
            Email
            <input type="email" value={form.email} onChange={set('email')} required autoComplete="email" />
          </label>
          <label>
            Телефон
            <input type="tel" value={form.phone} onChange={set('phone')} autoComplete="tel" />
          </label>
          <label>
            Пароль
            <input type="password" value={form.password} onChange={set('password')} required minLength={4} />
          </label>
          <label>
            Я
            <select value={form.role} onChange={set('role')}>
              <option value="passenger">Пассажир</option>
              <option value="reader">Водитель</option>
            </select>
          </label>
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn-block">
            Зарегистрироваться
          </button>
        </form>
        <p className="auth-footer">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  )
}

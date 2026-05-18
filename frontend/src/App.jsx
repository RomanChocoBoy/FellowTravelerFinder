import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import PassengerPage from './pages/PassengerPage'
import DriverPage from './pages/DriverPage'
import AdminPage from './pages/AdminPage'

function HomeRedirect() {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (user.role === 'passenger') return <Navigate to="/passenger" replace />
  if (user.role === 'reader') return <Navigate to="/driver" replace />
  if (user.role === 'admin') return <Navigate to="/admin" replace />
  return <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/passenger" element={<PassengerPage />} />
      <Route path="/driver" element={<DriverPage />} />
      <Route path="/admin" element={<AdminPage />} />
    </Routes>
  )
}

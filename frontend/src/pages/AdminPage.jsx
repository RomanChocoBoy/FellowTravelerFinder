import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import MobileShell from '../components/layout/MobileShell'
import ComplaintsList from '../components/admin/ComplaintsList'
import UsersList from '../components/admin/UsersList'

const TABS = [
  { id: 'complaints', label: 'Жалобы', short: 'Жалобы' },
  { id: 'users', label: 'Пользователи', short: 'Юзеры' },
]

export default function AdminPage() {
  const { user } = useAuth()
  const [tab, setTab] = useState('complaints')

  if (!user) return <Navigate to="/login" replace />
  if (user.role !== 'admin') return <Navigate to="/" replace />

  return (
    <MobileShell tabs={TABS} activeTab={tab} onTabChange={setTab} wide>
      {tab === 'complaints' && <ComplaintsList />}
      {tab === 'users' && <UsersList />}
    </MobileShell>
  )
}

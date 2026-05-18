import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import MobileShell from '../components/layout/MobileShell'
import PublishTrip from '../components/driver/PublishTrip'
import MyTrips from '../components/driver/MyTrips'
import PendingBookings from '../components/driver/PendingBookings'
import Chat from '../components/shared/Chat'
import ComplaintForm from '../components/shared/ComplaintForm'

const TABS = [
  { id: 'publish', label: 'Новая поездка', short: 'Создать' },
  { id: 'trips', label: 'Мои поездки', short: 'Поездки' },
  { id: 'pending', label: 'Заявки', short: 'Заявки' },
  { id: 'chat', label: 'Чат', short: 'Чат' },
  { id: 'complaint', label: 'Жалоба', short: 'Жалоба' },
]

export default function DriverPage() {
  const { user } = useAuth()
  const [tab, setTab] = useState('publish')
  const [refreshKey, setRefreshKey] = useState(0)

  if (!user) return <Navigate to="/login" replace />
  if (user.role !== 'reader') return <Navigate to="/" replace />

  return (
    <MobileShell tabs={TABS} activeTab={tab} onTabChange={setTab} wide={tab === 'chat'}>
      {tab === 'publish' && <PublishTrip onPublished={() => setRefreshKey((k) => k + 1)} />}
      {tab === 'trips' && <MyTrips refreshKey={refreshKey} />}
      {tab === 'pending' && <PendingBookings refreshKey={refreshKey} />}
      {tab === 'chat' && <Chat />}
      {tab === 'complaint' && <ComplaintForm />}
    </MobileShell>
  )
}

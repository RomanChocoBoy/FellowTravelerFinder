import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import MobileShell from '../components/layout/MobileShell'
import TripSearch from '../components/passenger/TripSearch'
import MyBookings from '../components/passenger/MyBookings'
import ReviewSection from '../components/passenger/ReviewSection'
import Chat from '../components/shared/Chat'
import ComplaintForm from '../components/shared/ComplaintForm'

const TABS = [
  { id: 'search', label: 'Поиск', short: 'Поиск' },
  { id: 'bookings', label: 'Бронирования', short: 'Брони' },
  { id: 'review', label: 'Отзывы', short: 'Отзывы' },
  { id: 'chat', label: 'Чат', short: 'Чат' },
  { id: 'complaint', label: 'Жалоба', short: 'Жалоба' },
]

export default function PassengerPage() {
  const { user } = useAuth()
  const [tab, setTab] = useState('search')

  if (!user) return <Navigate to="/login" replace />
  if (user.role !== 'passenger') return <Navigate to="/" replace />

  return (
    <MobileShell tabs={TABS} activeTab={tab} onTabChange={setTab} wide={tab === 'chat'}>
      {tab === 'search' && <TripSearch />}
      {tab === 'bookings' && <MyBookings />}
      {tab === 'review' && <ReviewSection />}
      {tab === 'chat' && <Chat />}
      {tab === 'complaint' && <ComplaintForm />}
    </MobileShell>
  )
}

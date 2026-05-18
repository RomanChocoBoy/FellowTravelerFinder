const API = import.meta.env.VITE_API_URL || 'http://localhost:5000'

async function request(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.error || 'Ошибка сервера')
  }
  return data
}

export const api = {
  register: (body) => request('/api/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  login: (body) => request('/api/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  searchTrips: (from, to) =>
    request(`/api/trips/search?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`),
  myTrips: (driverId) => request(`/api/trips/my?driver_id=${driverId}`),
  publishTrip: (body) => request('/api/trips', { method: 'POST', body: JSON.stringify(body) }),
  deleteTrip: (tripId, driverId) =>
    request(`/api/trips/${tripId}?driver_id=${driverId}`, { method: 'DELETE' }),
  bookings: (passengerId) => request(`/api/bookings?passenger_id=${passengerId}&detailed=1`),
  pendingBookings: (driverId) => request(`/api/bookings/pending?driver_id=${driverId}`),
  reviewableTrips: (passengerId) => request(`/api/bookings/reviewable?passenger_id=${passengerId}`),
  createBooking: (body) => request('/api/bookings', { method: 'POST', body: JSON.stringify(body) }),
  approveBooking: (id) => request(`/api/bookings/${id}/approve`, { method: 'POST' }),
  cancelBooking: (id) => request(`/api/bookings/${id}/cancel`, { method: 'POST' }),
  tripContacts: (userId) => request(`/api/users/trip-contacts?user_id=${userId}`),
  chatThreads: (userId) => request(`/api/chat/threads?user_id=${userId}`),
  messages: (userId, otherId, tripId) => {
    let url = `/api/messages?user_id=${userId}&other_id=${otherId}&trip_id=${tripId}`
    return request(url)
  },
  sendMessage: (body) => request('/api/messages', { method: 'POST', body: JSON.stringify(body) }),
  createReview: (body) => request('/api/reviews', { method: 'POST', body: JSON.stringify(body) }),
  complaints: () => request('/api/complaints?detailed=1'),
  createComplaint: (body) => request('/api/complaints', { method: 'POST', body: JSON.stringify(body) }),
  approveComplaint: (id) => request(`/api/complaints/${id}/approve`, { method: 'POST' }),
  rejectComplaint: (id) => request(`/api/complaints/${id}/reject`, { method: 'POST' }),
  allUsers: () => request('/api/users'),
  blockUser: (id) => request(`/api/users/${id}/block`, { method: 'POST' }),
  unblockUser: (id) => request(`/api/users/${id}/unblock`, { method: 'POST' }),
}

export function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function todayInputValue() {
  return new Date().toISOString().slice(0, 10)
}

import { Navigate } from 'react-router-dom'
import { getAccessToken } from '../services/api'

// Yeh component check karega ke user authenticated hai ya nahi
export default function ProtectedRoute({ children }) {
  const token = getAccessToken()

  // Agar token nahi hai, toh user ko login page par bhejo
  if (!token) {
    return <Navigate to="/login" replace />
  }

  // Agar token hai, toh protected page render karo
  return children
}
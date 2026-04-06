import { Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-dvh items-center justify-center text-muted-foreground">
        Loading...
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute

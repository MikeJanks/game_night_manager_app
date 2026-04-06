import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { authenticatedFetch, setToken, removeToken, getToken } from '@/lib/api'
import loginApi from '@/apis/login'
import signupApi from '@/apis/signup'

const AuthContext = createContext(null)

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  const fetchCurrentUser = useCallback(async () => {
    try {
      const res = await authenticatedFetch('/api/auth/me')
      if (res.ok) {
        const data = await res.json()
        setUser(data)
        setIsAuthenticated(true)
        return data
      }

      if (res.status === 401) {
        removeToken()
        setUser(null)
        setIsAuthenticated(false)
      }
    } catch (err) {
      console.error('Failed to fetch current user', err)
    }
    return null
  }, [])

  useEffect(() => {
    const token = getToken()
    if (!token) {
      setIsLoading(false)
      return
    }

    fetchCurrentUser().finally(() => setIsLoading(false))
  }, [fetchCurrentUser])

  const login = async (username, password) => {
    const data = await loginApi({ username, password })

    if (!data.access_token) {
      throw new Error('No access token received')
    }

    setToken(data.access_token)
    setIsAuthenticated(true)

    const userData = await fetchCurrentUser()
    return { success: true, user: userData }
  }

  const signup = async (username, email, password) => {
    await signupApi({ username, email, password })

    const loginResult = await login(username, password)
    if (!loginResult.success) {
      throw new Error('Signup succeeded but login failed')
    }

    setUser(loginResult.user)
    return { success: true, user: loginResult.user }
  }

  const logout = () => {
    removeToken()
    setUser(null)
    setIsAuthenticated(false)
    navigate('/login', { replace: true })
  }

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    signup,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

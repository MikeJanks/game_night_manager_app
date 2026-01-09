// Basic API utilities for the frontend

const API_BASE_URL = `http://${window.location.hostname}:8000`
const TOKEN_KEY = 'auth_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY) || null

export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token)
}

export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY)
}

// Helper function to ensure URL starts with /api prefix
const ensureApiPrefix = (url) => {
  if (url.startsWith('/api')) {
    return url
  }
  return `/api${url.startsWith('/') ? url : `/${url}`}`
}

export const authenticatedFetch = async (url, options = {}) => {
  const token = getToken()

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const apiUrl = ensureApiPrefix(url)
  return fetch(`${API_BASE_URL}${apiUrl}`, {
    ...options,
    headers,
  })
}

export const publicFetch = async (url, options = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }

  const apiUrl = ensureApiPrefix(url)
  return fetch(`${API_BASE_URL}${apiUrl}`, {
    ...options,
    headers,
  })
}

export { API_BASE_URL }


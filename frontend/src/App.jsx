import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './components/Login'
import Signup from './components/Signup'
import Chat from './components/Chat'
import LandingPage from './pages/landing/LandingPage'
import ChatPageV2 from './pages/chat/ChatPageV2'

const App = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="h-dvh w-full font-body antialiased bg-canvas">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/" element={<LandingPage />} />
            <Route
              path="/chat"
              element={
                <ProtectedRoute>
                  <Chat />
                </ProtectedRoute>
              }
            />
            <Route path="/v2/chat" element={ <ChatPageV2 /> } />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App


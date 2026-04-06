import React from "react"
import ReactDOM from "react-dom/client"
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import "./index.css"

import { AuthProvider } from "./contexts/AuthContext"
import ProtectedRoute from "./components/ProtectedRoute"
import LandingPage from "./pages/landing/LandingPage"
import ChatPage from "./pages/chat/ChatPage"
import LoginPage from "./pages/login/LoginPage"
import SignupPage from "./pages/signup/SignupPage"

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-dvh w-full font-body antialiased bg-background">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
)
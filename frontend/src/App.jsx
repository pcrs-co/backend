import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Header from './components/layout/Header'
import Home from './components/pages/Home'
import Login from './components/pages/Login'
import Register from './components/pages/Register'
import NotFound from './components/pages/NotFound'

function Logout() {
  useEffect(() => {
    localStorage.clear()
  }, [])
  return <Navigate to="/login" />
}

function RegisterAndLogout() {
  useEffect(() => {
    localStorage.clear()
  }, [])
  return <Register />
}

function App() {
  return (
    <BrowserRouter>
      <Header /> {/* This stays visible across all routes */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/register" element={<RegisterAndLogout />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

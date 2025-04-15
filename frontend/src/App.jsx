import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppToastContainer from '../features/Toastcontainer.jsx'
import Register from './components/pages/Register'
import NotFound from './components/pages/NotFound'
import Header from './components/layout/Header'
import Login from './components/pages/Login'
import Home from './components/pages/Home'
import React, { useEffect } from 'react'

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
      <AppToastContainer />
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

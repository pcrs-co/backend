import {
  BrowserRouter as Router,
  Routes,
  Route
} from 'react-router-dom'
import AppToastContainer from './components/features/Toastcontainer'
// import React, { useEffect } from 'react'
import PublicLayout from './components/layout/PublicLayout'

// public pages
import Home from './components/pages/public/Home'
import Register from './components/pages/public/Register'
import Login from './components/pages/public/Login'
import NotFound from '.components/pages/public/NotFound'
import DeviceDetails from './components/pages/public/DeviceDetails'
import DeviceList from './components/pages/public/DeviceList'
import InputBasic from './components/pages/public/InputBasic'
import InputAdvanced from './components/pages/public/InputAdvanced'
import Specs from './components/pages/public/Specs'
import VendorProfile from './components/pages/public/VendorProfile'

// customer pages
// import Profile from './components/pages/customer/Profile'

// function Logout() {
//   useEffect(() => {
//     localStorage.clear()
//   }, [])
//   return <Navigate to="/login" />
// }

// function RegisterAndLogout() {
//   useEffect(() => {
//     localStorage.clear()
//   }, [])
//   return <Register />
// }

function App() {
  return (

    <Router>
      <AppToastContainer />
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<PublicLayout />}>
          <Route index element={<Home />} />
          <Route path="specs" element={<Specs />} />
          <Route path="devices" element={<DeviceList />} />
          <Route path="devices/:id" element={<DeviceDetails />} />
          <Route path="input-basic" element={<InputBasic />} />
          <Route path="input-advanced" element={<InputAdvanced />} />
          <Route path="vendor-profile" element={<VendorProfile />} />
          <Route path="*" element={<NotFound />} />
        </Route>

        {/* Auth routes */}
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </Router>

  )
}

export default App


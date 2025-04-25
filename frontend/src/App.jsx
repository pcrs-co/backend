import {
  BrowserRouter as Router,
  Routes,
  Route
} from 'react-router-dom'
import AppToastContainer from './features/Toastcontainer'
// import React, { useEffect } from 'react'

// Layouts
import PublicLayout from './components/layout/PublicLayout'
import VendorLayout from './components/layout/vendor/VendorLayout';

// public pages
import Home from './pages/public/Home'
import Register from './pages/public/Register'
import Login from './pages/public/Login'
import NotFound from './pages/public/NotFound'
import DeviceDetails from './pages/public/DeviceDetails'
import DeviceList from './pages/public/DeviceList'
import InputBasic from './pages/public/InputBasic'
import InputAdvanced from './pages/public/InputAdvanced'
import Specs from './pages/public/Specs'
import VendorProfile from './pages/public/VendorProfile'

// Vendor pages
import { Dashboard as VendorDashboard } from './pages/vendor/Dashboard';
import ProductList from './pages/vendor/ProductList';
import ProductForm from './pages/vendor/ProductForm';
import ProductDetails from './pages/vendor/ProductDetails';

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

        {/* Vendor Routes */}
        <Route path="/vendor" element={<VendorLayout />}>
          <Route path="dashboard" element={<VendorDashboard />} />
          <Route path="products" element={<ProductList />} />
          <Route path="products/create" element={<ProductForm />} />
          <Route path="products/:id" element={<ProductDetails />} />
        </Route>

      </Routes>
    </Router>

  )
}

export default App


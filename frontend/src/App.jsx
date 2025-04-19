// import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
// import AppToastContainer from './components/features/Toastcontainer'
// import React, { useEffect } from 'react'

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
    
    // <BrowserRouter>
    //   <AppToastContainer />
    //   <Routes>
    //   </Routes>
    // </BrowserRouter>

    <div className="container mt-5">
      <h1>Welcome to PCRS</h1>
      <p>Let's recommend some laptops.</p>
    </div>  
    
  )
}

export default App


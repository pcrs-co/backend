import react from 'react'
import { BrowserRouter , Routes, Route, Navigate } from 'react-router-dom'
import Home from './components/pages/Home'
import Login from './components/pages/Login'
import Register from './components/pages/Register'
import NotFound from './components/pages/NotFound'
// import ProtectedRoute from './components/features/ProtectedRoute'

function Logout() {
    localStorage.clear()
    return <Navigate to="/login" />
  }
  
  function RegisterAndLogout() {
    localStorage.clear()
    return <Register />
  }
  
  function App() {
    return (
      <BrowserRouter>
        <Routes>
          <Route
            path="/home"
            element={
            //   <ProtectedRoute>
                <Home />
            //   </ProtectedRoute>
            }
          />
          <Route path="/login" element={<Login />} />
          <Route path="/logout" element={<Logout />} />
          <Route path="/register" element={<RegisterAndLogout />} />
          <Route path="*" element={<NotFound />}></Route>
        </Routes>
      </BrowserRouter>
    )
  }
  
  export default App
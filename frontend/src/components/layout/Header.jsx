import { Routes, Route } from 'react-router-dom'
import NavigationBar from '../features/NavigationBar'
import Home from '../pages/Home.jsx'
import Login from '../pages/Login.jsx'
import Register from '../pages/Register.jsx'

/**
 * The main header component for the application.
 * 
 * This component renders the navigation bar at the top of the page,
 * and defines the routes for the application.
 */
function Header() {

    return (
      <>
          {/* The navigation bar at the top of the page. */}
          <NavigationBar />
          {/* The routes for the application. */}
          <Routes>
            {/* The home page route. */}
            <Route path="/" element={<Home />} />
            {/* The login page route. */}
            <Route path="/login" element={<Login />} />
            {/* The register page route. */}
            <Route path="/register" element={<Register />} />
          </Routes>
      </>
    );
}

export default Header

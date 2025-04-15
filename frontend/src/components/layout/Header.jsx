import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import NavigationBar from '../features/NavigationBar'
import Home from '../pages/Home.jsx'
import Login from '../pages/Login.jsx'
import Register from '../pages/Register.jsx'

function Footer() {

    return (
      <>
        <Router>
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </Router>
      </>
    );
}

export default Footer
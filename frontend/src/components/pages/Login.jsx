import { ACCESS_TOKEN, REFRESH_TOKEN } from '../../utils/constants.js'
import AppToastContainer from '../features/Toastcontainer.jsx'
// import styles from '../../styles/pages/LoginPage.module.css'
import { useNavigate } from "react-router-dom"
import Header from '../layout/Header.jsx'
import Footer from '../layout/Footer.jsx'
import { toast } from 'react-toastify'
import { useState } from 'react'
import api from '../utils/api'

// The Login component handles user login
function Login() {
    // State variables to store the username and password
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")

    // Use the useNavigate hook to get the navigate function
    const navigate = useNavigate()

    // Function to handle form submission
    const handleSubmit = async (e) => {
        // Prevent the default form submission behavior
        e.preventDefault()

        if (!username || !password) {
            toast.error("Username and Password are required")
        }

        try {
            // Make a POST request to the server to log in the user
            const response = await api.post("/api/token", { username, password })

            // Save the access and refresh tokens in local storage
            localStorage.setItem(ACCESS_TOKEN, response.data.access)
            localStorage.setItem(REFRESH_TOKEN, response.data.refresh)

            toast.success("Login successful!")

            // Redirect the user to the home page or dashboard
            navigate("/")
        } catch (error) {
            // Catch any errors and display an error message
            console.error("Login error:", error)
            toast.error("Invalid Credentials. Please try again.")
        }
    }

    // Render the Login component
    return (
        <>
            <AppToastContainer />
            <Header />

            <div className={styles.loginContainer}>
                <h1>Login</h1>

                <form className={styles.loginForm} onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <button type="submit">
                        Login
                    </button>
                </form>
            </div>

            <Footer />
        </>
    )
}

export default Login


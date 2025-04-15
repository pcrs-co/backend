import { ACCESS_TOKEN, REFRESH_TOKEN } from '../../utils/constants.js'
import styles from '../../styles/pages/LoginPage.module.css'
import { useNavigate } from "react-router-dom"
import Header from '../layout/Header.jsx'
import Footer from '../layout/Footer.jsx'
import { useState } from 'react'
import api from '../utils/api'

// The Login component handles user login
function Login() {
    // State variables to store the username and password
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")

    // State variable to store any error messages
    const [error, setError] = useState(null)

    // Use the useNavigate hook to get the navigate function
    const navigate = useNavigate()

    // Function to handle form submission
    const handleSubmit = async (e) => {
        // Prevent the default form submission behavior
        e.preventDefault()

        // Reset the error message
        setError(null)

        try {
            // Make a POST request to the server to log in the user
            const response = await api.post("/api/token", { username, password })

            // Save the access and refresh tokens in local storage
            localStorage.setItem(ACCESS_TOKEN, response.data.access)
            localStorage.setItem(REFRESH_TOKEN, response.data.refresh)

            // Redirect the user to the home page or dashboard
            navigate("/")
        } catch (err) {
            // Catch any errors and display an error message
            console.error("Login error:", err)
            setError("Invalid Username or Password")
        }
    }

    // Render the Login component
    return (
        <>
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

                {error && <p style={{ color: "red" }}>{error}</p>}
            </div>

            <Footer />
        </>
    )
}

export default Login


import { ACCESS_TOKEN, REFRESH_TOKEN } from '../../utils/constants.js'
import styles from '../../styles/pages/LoginPage.module.css'
import { useNavigate } from "react-router-dom"
import Header from '../layout/Header.jsx'
import Footer from '../layout/Footer.jsx'
import { useState } from 'react'
import api from '../utils/api'

function Login() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState(null)
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError(null)
        try {
            const response = await api.post("/api/token", { username, password })

            //save tokens
            localStorage.setItem(ACCESS_TOKEN, response.data.access)
            localStorage.setItem(REFRESH_TOKEN, response.data.refresh)

            //Redirect to home or dashboard
            navigate("/")
        } catch (err) {
            console.error("Login error:", err)
            setError("Invalid Username or Password")
        }
    }



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

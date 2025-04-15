// import styles from '../../styles/pages/RegisterPage.module.css'
import AppToastContainer from '../features/Toastcontainer.jsx'
import { useNavigate } from "react-router-dom"
import Header from '../layout/Header.jsx'
import Footer from '../layout/Footer.jsx'
import { toast } from 'react-toastify'
import { useState } from 'react'
import api from '../../utils/api.js'


function Register() {
    const [first_name, setFirst_name] = useState("")
    const [last_name, setLast_name] = useState("")
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [phone_number, setPhone_number] = useState("")
    const [date_of_birth, setDate_of_birth] = useState("")
    const [region, setRegion] = useState("")
    const [district, setDistrict] = useState("")
    const [password, setPassword] = useState("")
    const [password2, setPassword2] = useState("")

    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        // Prevent the default form submission behavior
        e.preventDefault()

        if (!first_name || !last_name || !username || !email || !phone_number || !date_of_birth || !region || !district || !password || !password2) {
            toast.error("All fields are required")
            return
        }

        if (password !== password2) {
            toast.error("Passwords do not match")
            return
        }

        try {
            // Make a POST request to the server to log in the user
            const response = await api.post("/api/register/", {
                first_name,
                last_name,
                username,
                email,
                phone_number,
                date_of_birth,
                region,
                district,
                password,
                password2,
            })

            toast.success("Registration successful!")
            navigate("/login")
        } catch (error) {
            // Catch any errors and display an error message
            console.error("Registration error:", error)
            toast.error("Registration failed. Please check your inputs.")
        }
    }
    return (
        <>
            <AppToastContainer />
            <Header />

            <div className={styles.registerContainer}>
                <h1>Register</h1>
                <form className={styles.registerForm} onSubmit={handleSubmit}>
                    <input type="text" placeholder="First Name" value={first_name} onChange={e => setFirst_name(e.target.value)} />
                    <input type="text" placeholder="Last Name" value={last_name} onChange={e => setLast_name(e.target.value)} />
                    <input type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
                    <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
                    <input type="tel" placeholder="Phone Number" value={phone_number} onChange={e => setPhone_number(e.target.value)} />
                    <input type="date" placeholder="Date Of Birth" value={date_of_birth} onChange={e => setDate_of_birth(e.target.value)} />
                    <input type="text" placeholder="Region" value={region} onChange={e => setRegion(e.target.value)} />
                    <input type="text" placeholder="District" value={district} onChange={e => setDistrict(e.target.value)} />
                    <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
                    <input type="password" placeholder="Confirm Password" value={password2} onChange={e => setPassword2(e.target.value)} />
                    <button type="submit">Register</button>
                </form>
            </div>

            <Footer />
        </>
    )
}

export default Register

import { REFRESH_TOKEN, ACCESS_TOKEN } from "./constants"
import { Navigate } from "react-router-dom"
import { jwtDecode } from "jwt-decode"
import { useState, useEffect } from "react"
import api from './utils/api'

// This component is used to protect routes from unauthorized access
function ProtectedRoute({ children }) {
    // State to keep track of whether the user is authorized or not
    const [isAuthorized, setIsAuthorized] = useState(null)

    // Run the auth function when the component mounts
    useEffect(() => {
        auth().catch(() => setIsAuthorized(false))
    }, [])

    // Function to refresh the access token
    const refreshToken = async () => {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN)
        try {
            // Make a request to the server to refresh the token
            const res = await api.post("/api/token/refresh", { refresh: refreshToken })
            if (res.status === 200) {
                // If the request is successful, update the access token
                localStorage.setItem(ACCESS_TOKEN, res.data.access)
                setIsAuthorized(true)
            } else {
                // If the request fails, set isAuthorized to false
                setIsAuthorized(false)
            }
        } catch (error) {
            // If there is an error, set isAuthorized to false
            console.log(error)
            setIsAuthorized(false)
        }
    }

    // Function to check if the user is authorized
    const auth = async () => {
        const token = localStorage.getItem(ACCESS_TOKEN)
        if (!token) {
            // If there is no token, set isAuthorized to false
            setIsAuthorized(false)
            return
        }
        const decoded = jwtDecode(token)
        const tokenExpiration = decoded.exp
        const now = Date.now() / 1000

        // If the token has expired, refresh it
        if (tokenExpiration < now) {
            await refreshToken()
        } else {
            // If the token has not expired, set isAuthorized to true
            setIsAuthorized(true)
        }
    }

    // If isAuthorized is null, return a loading message
    if (isAuthorized === null) {
        return <div>loading...</div>
    }

    // If isAuthorized is true, return the children, otherwise redirect to /login
    return isAuthorized ? children : <Navigate to="/login" />
}

export default ProtectedRoute

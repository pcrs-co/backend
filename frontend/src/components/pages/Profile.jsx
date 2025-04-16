import { useState, useEffect } from "react"
import api from "../../utils/api"
import { ACCESS_TOKEN } from "../../utils/constants"

function Profile () {
    const [username, setUsername] = useState("")
    const [first_name, setFirst_name] = useState("")
    const [last_name, setLast_name] = useState("")
    const [email, setEmail] = useState("")
    const [phone_number, setPhone_number] = useState("")
    const [region, setRegion] = useState("")
    const [district, setDistrict] = useState("")
    const [date_of_birth, setDate_of_birth] = useState("")

    useEffect(() => {
        const token = localStorage.getItem(ACCESS_TOKEN)
        if (token) {
            api.get("/api/user/me/", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            .then(res => {
                setUsername(res.data.username)
                setFirst_name(res.data.first_name)
                setLast_name(res.data.last_name)
                setEmail(res.data.email)
                setPhone_number(res.data.phone_number)
                setRegion(res.data.region)
                setDistrict(res.data.district)
                setDate_of_birth(res.data.date_of_birth)
            })
            .catch(err => {
                console.log(err)
            })
        }
    }, [])

    return (
        <>
            <h1>Profile</h1>
            <p>Username: {username}</p>
            <p>First Name: {first_name}</p>
            <p>Last Name: {last_name}</p>
            <p>Email: {email}</p>
            <p>Phone Number: {phone_number}</p>
            <p>Region: {region}</p>
            <p>District: {district}</p>
            <p>Date of Birth: {date_of_birth}</p>
        </>
    )
}



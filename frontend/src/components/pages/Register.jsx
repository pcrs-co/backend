// Import necessary components and libraries
import AppToastContainer from "../features/Toastcontainer.jsx";
import { useNavigate } from "react-router-dom";
import Header from "../layout/Header.jsx";
import Footer from "../layout/Footer.jsx";
import { toast } from "react-toastify";
import api from "../../utils/api.js";
import { useState } from "react";

// Register component for user registration
function Register() {
  // State variables for form input values
  const [first_name, setFirst_name] = useState("");
  const [last_name, setLast_name] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [phone_number, setPhone_number] = useState("");
  const [date_of_birth, setDate_of_birth] = useState("");
  const [region, setRegion] = useState("");
  const [district, setDistrict] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");

  const navigate = useNavigate(); // Hook for navigation

  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission

    // Validate input fields
    if (
      !first_name ||
      !last_name ||
      !username ||
      !email ||
      !phone_number ||
      !date_of_birth ||
      !region ||
      !password ||
      !password2
    ) {
      toast.error("All fields are required");
      return;
    }

    // Check if passwords match
    if (password !== password2) {
      toast.error("Passwords do not match");
      return;
    }

    try {
      // Make API call to register the user
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
      });

      // Display success message and navigate to login
      toast.success("Registration successful!");
      navigate("/login");
    } catch (error) {
      if (error.response && error.response.data) {
        const errors = error.response.data;

        // Loop through all error fields and show them
        for (const key in errors) {
          if (Array.isArray(errors[key])) {
            errors[key].forEach((msg) => toast.error(`${key}: ${msg}`));
          } else {
            toast.error(`${key}: ${errors[key]}`);
          }
        }
      } else {
        toast.error("Registration failed. Please check your inputs.");
      }
      console.error("Registration error:", error);
    }

  };

  // Render the registration form
  return (
    <>
      <div>
        <h1>Register</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="First Name"
            value={first_name}
            onChange={(e) => setFirst_name(e.target.value)}
          />
          <input
            type="text"
            placeholder="Last Name"
            value={last_name}
            onChange={(e) => setLast_name(e.target.value)}
          />
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="tel"
            placeholder="Phone Number"
            value={phone_number}
            onChange={(e) => setPhone_number(e.target.value)}
          />
          <input
            type="date"
            placeholder="Date Of Birth"
            value={date_of_birth}
            onChange={(e) => setDate_of_birth(e.target.value)}
          />
          <input
            type="text"
            placeholder="Region"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
          />
          <input
            type="text"
            placeholder="District"
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <input
            type="password"
            placeholder="Confirm Password"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
          />
          <button type="submit">Register</button>
        </form>
      </div>
      <Footer />
    </>
  );
}

export default Register;


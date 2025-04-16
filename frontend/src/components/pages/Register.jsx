// Import necessary components and libraries
import { useState, useRef, useEffect } from "react";
import intlTelInput from "intl-tel-input";
import { useNavigate } from "react-router-dom";
import Footer from "../layout/Footer.jsx";
import { toast } from "react-toastify";
import api from "../../utils/api.js";

// Register component for user registration
function Register() {
  // State variables for form input values
  const [first_name, setFirst_name] = useState("");
  const [last_name, setLast_name] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const phoneInputRef = useRef(null)
  const itiRef = useRef(null); // ✅ ADDED: to hold intlTelInput instance
  const [date_of_birth, setDate_of_birth] = useState("");
  const [region, setRegion] = useState("");
  const [district, setDistrict] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");

  useEffect(() => {
    if (phoneInputRef.current) {
      itiRef.current = intlTelInput(phoneInputRef.current, { // 🔧 UPDATED
        initialCountry: 'auto',
        geoIpLookup: function (callback) {
          fetch('https://ipinfo.io/json?token=YOUR_TOKEN_HERE')
            .then((resp) => resp.json())
            .then((resp) => callback(resp.country))
            .catch(() => callback('us'));
        },
        nationalMode: false,
        separateDialCode: false,
        preferredCountries: ['us', 'gb', 'ke'],
        utilsScript:
          'https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.19/js/utils.js',
      });
    }
  }, []);

  const navigate = useNavigate(); // Hook for navigation

  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission

    // 🔧 UPDATED: Use local `itiRef.current` safely
    const fullPhoneNumber = itiRef.current?.getNumber() || phoneInputRef.current?.value;

    // Validate input fields
    if (
      !first_name ||
      !last_name ||
      !username ||
      !email ||
      !fullPhoneNumber ||
      !date_of_birth ||
      !region ||
      !password ||
      !password2
    ) {
      toast.error("All fields are required except district");
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
        phone_number: fullPhoneNumber,
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
      } else if (!error.response) {
        toast.error("Server not reachable. Is it running?");
      } else if (error.response.status === 401) {
        toast.error("Registration failed. Please check your inputs.");
      } else {
        toast.error("Unexpected error occurred!")
      }
      console.error("Registration error:", error);
    }

  };

  // Render the registration form
  return (
    <>
      <div className='container mt-3 mb-3 justify-content-center text-center'>
        <h2>Register</h2>
        <form onSubmit={handleSubmit}>
          <div className="row mt-3">
            <div className="col">
              <input
                className="form-control"
                type="text"
                placeholder="First Name"
                value={first_name}
                onChange={(e) => setFirst_name(e.target.value)}
              />
            </div>
            <div className="col">
              <input
                className="form-control"
                type="text"
                placeholder="Last Name"
                value={last_name}
                onChange={(e) => setLast_name(e.target.value)}
              />
            </div>
          </div>
          <div className="row mt-3">
            <div className="col">
              <input
                className="form-control"
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="col">
              <input
                className="form-control"
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>
          <div className="row mt-3">
            <div className="col">
              <input
                id="phone"
                ref={phoneInputRef}
                className="form-control"
                type="tel"
                placeholder="Phone Number"
              />
            </div>
            <div className="col">
              <input
                className="form-control"
                type="date"
                placeholder="Date Of Birth"
                value={date_of_birth}
                onChange={(e) => setDate_of_birth(e.target.value)}
              />
            </div>
          </div>
          <div className="row mt-3">
            <div className="col">
              <input
                className="form-control"
                type="text"
                placeholder="Region"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              />
            </div>
            <div className="col">
              <input
                className="form-control"
                type="text"
                placeholder="District"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
              />
            </div>
          </div>
          <div className="row mt-3">
            <div className="col">
              <input
                className="form-control"
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="col">
              <input
                className="form-control"
                type="password"
                placeholder="Confirm Password"
                value={password2}
                onChange={(e) => setPassword2(e.target.value)}
              />
            </div>
          </div>
          <button className="btn btn-outline-secondary mt-3 mb-3" type="submit">Register</button>
        </form>
      </div>
      <Footer />
    </>
  );
}

export default Register;


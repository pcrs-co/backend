import { useState, useRef, useEffect } from "react";
import intlTelInput from "intl-tel-input";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../../utils/api";
import { Link } from "react-router-dom";
import Button from "../../features/ReusableButton.jsx";
import { Input, Ripple, initMDB } from "mdb-ui-kit";

function Register() {
  const [first_name, setFirst_name] = useState("");
  const [last_name, setLast_name] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const phoneInputRef = useRef(null);
  const itiRef = useRef(null);
  const [date_of_birth, setDate_of_birth] = useState("");
  const [region, setRegion] = useState("");
  const [district, setDistrict] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    initMDB({ Input, Ripple });

    if (phoneInputRef.current) {
      itiRef.current = intlTelInput(phoneInputRef.current, {
        initialCountry: "auto",
        geoIpLookup: function (callback) {
          fetch("https://ipinfo.io/json?token=YOUR_TOKEN_HERE")
            .then((resp) => resp.json())
            .then((resp) => callback(resp.country))
            .catch(() => callback("us"));
        },
        nationalMode: false,
        separateDialCode: false,
        preferredCountries: ["us", "gb", "ke"],
        utilsScript:
          "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.19/js/utils.js",
      });
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const fullPhoneNumber =
      itiRef.current?.getNumber() || phoneInputRef.current?.value;

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
      toast.error("Please fill required fields");
      return;
    }

    if (password !== password2) {
      toast.error("Passwords do not match");
      return;
    }

    try {
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

      toast.success("Registration successful!");
      navigate("/login");
    } catch (error) {
      if (error.response && error.response.data) {
        const errors = error.response.data;
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
        toast.error("Unexpected error occurred!");
      }
      console.error("Registration error:", error);
    }
  };

  return (
    <>
      <div className="container mt-3">
        <Button to="/" variant="outline-primary" className="d-inline-flex align-items-center">
          Home
        </Button>
      </div>

      <div className="container mt-5 mb-3 d-flex flex-column align-items-center w-75">
        <h2 className="mb-4">Register</h2>
        <form onSubmit={handleSubmit} className="w-100">
          <div className="row">
            <div className="col form-outline mb-4">
              <label className="form-label" htmlFor="firstName">
                First Name
              </label>
              <input
                type="text"
                id="firstName"
                className="form-control"
                placeholder="e.g. John"
                value={first_name}
                onChange={(e) => setFirst_name(e.target.value)}
              />
            </div>
            <div className="col form-outline mb-4">
              <label className="form-label" htmlFor="lastName">
                Last Name
              </label>
              <input
                type="text"
                id="lastName"
                className="form-control"
                placeholder="e.g. Doe"
                value={last_name}
                onChange={(e) => setLast_name(e.target.value)}
              />
            </div>
          </div>

          <div className="row">
            <div className="col form-outline mb-4">
              <label className="form-label" htmlFor="username">
                Username
              </label>
              <input
                type="text"
                id="username"
                className="form-control"
                placeholder="e.g. johndoe"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
              />
            </div>
            <div className="col form-outline mb-4">
              <label className="form-label" htmlFor="email">
                Email
              </label>
              <input
                type="email"
                id="email"
                className="form-control"
                placeholder="e.g. johndoe@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>
          </div>

          <div className="row">
            <div className="col form-outline mb-4">
              <label className="form-label" htmlFor="phone">
                Phone Number
              </label>
              <input
                type="tel"
                id="phone"
                ref={phoneInputRef}
                className="form-control"
                placeholder="e.g. +254 701 234 567"
              />
            </div>
            <div className="col form-outline mb-4">
              <label className="form-label" htmlFor="dob">
                Date of Birth
              </label>
              <input
                type="date"
                id="dob"
                className="form-control"
                value={date_of_birth}
                onChange={(e) => setDate_of_birth(e.target.value)}
              />
            </div>
          </div>

          <div className="row">
            <div className="col form-outline mb-4">
              <label className="form-label" htmlFor="region">
                Region
              </label>
              <input
                type="text"
                id="region"
                className="form-control"
                placeholder="e.g. Nairobi"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              />
            </div>
            <div className="col form-outline mb-4">
              <label className="form-label" htmlFor="district">
                District (optional)
              </label>
              <input
                type="text"
                id="district"
                className="form-control"
                placeholder="e.g. Kiambu"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
              />
            </div>
          </div>

          <div className="row">
            <div className="col form-outline mb-4">
              <label className="form-label" htmlFor="password">
                Password
              </label>
              <input
                type="password"
                id="password"
                className="form-control"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="new-password"
              />
            </div>
            <div className="col form-outline mb-4">
              <label className="form-label" htmlFor="password2">
                Confirm Password
              </label>
              <input
                type="password"
                id="password2"
                className="form-control"
                value={password2}
                onChange={(e) => setPassword2(e.target.value)}
                autoComplete="new-password"
              />
            </div>
          </div>

          {/* Submit */}
          <Button type="submit" className="w-100 mb-3">
            Register
          </Button>

          <div>
            <Link
              to="/login"
              style={{ color: "#0d6efd" }}
              className="text-decoration-none"
              onMouseOver={(e) => (e.target.style.color = "#0b5ed7")}
              onMouseOut={(e) => (e.target.style.color = "#0d6efd")}
            >
              Already have an account?
            </Link>
          </div>
        </form>
      </div>
    </>
  );
}

export default Register;



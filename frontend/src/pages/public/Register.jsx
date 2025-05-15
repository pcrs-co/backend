import { useState, useRef, useEffect } from "react";
import intlTelInput from "intl-tel-input";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../../utils/api";
import { Link } from "react-router-dom";
import Button from "../../features/ReusableButton.jsx";
import { Input, Ripple, initMDB } from "mdb-ui-kit";
import "./Register.css";

function Register() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    username: "",
    email: "",
    date_of_birth: "",
    region: "",
    district: "",
    password: "",
    password2: ""
  });

  const phoneInputRef = useRef(null);
  const itiRef = useRef(null);
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

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const validateStep = () => {
    const { first_name, last_name, username, email, date_of_birth, region, password, password2 } = formData;

    switch (step) {
      case 1:
        if (!first_name || !last_name) {
          toast.error("Please enter first and last name.");
          return false;
        }
        break;
      case 2:
        if (!username) {
          toast.error("Username is required.");
          return false;
        }
        break;
      case 3:
        const phone = itiRef.current?.getNumber() || phoneInputRef.current?.value;
        if (!email || !phone || !date_of_birth || !region) {
          toast.error("Complete all required fields.");
          return false;
        }
        break;
      case 4:
        // district is optional
        break;
      case 5:
        if (!password || !password2) {
          toast.error("Enter and confirm password.");
          return false;
        }
        if (password !== password2) {
          toast.error("Passwords do not match.");
          return false;
        }
        break;
    }
    return true;
  };

  const handleNext = () => {
    if (validateStep()) setStep((prev) => prev + 1);
  };

  const handlePrev = () => {
    setStep((prev) => prev - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateStep()) return;

    const fullPhoneNumber = itiRef.current?.getNumber() || phoneInputRef.current?.value;

    try {
      await api.post("/api/register/", {
        ...formData,
        phone_number: fullPhoneNumber
      });

      toast.success("Registration successful!");
      navigate("/login");
    } catch (error) {
      if (error.response?.data) {
        Object.entries(error.response.data).forEach(([key, value]) => {
          toast.error(`${key}: ${Array.isArray(value) ? value.join(", ") : value}`);
        });
      } else {
        toast.error("Unexpected error occurred!");
      }
    }
  };

  return (
    <>
      <div className="container mt-3">
        <Button to="/" variant="outline-primary">Home</Button>
      </div>

      <div className="container mt-5 mb-3 d-flex flex-column align-items-center w-75">
        <h2 className="mb-2">Register</h2>
        <p className="text-muted">Step {step} of 5</p>

        <form onSubmit={handleSubmit} className="w-100">
          {/* Step 1 - Names */}
          <div className={`fade-step ${step === 1 ? "show" : "hide"}`}>
            <div className="row">
              <div className="col mb-4">
                <label className="form-label">First Name</label>
                <input type="text" name="first_name" className="form-control" value={formData.first_name} onChange={handleChange} />
              </div>
              <div className="col mb-4">
                <label className="form-label">Last Name</label>
                <input type="text" name="last_name" className="form-control" value={formData.last_name} onChange={handleChange} />
              </div>
            </div>
            <div className="row">
              <div className="col mb-4">
                <label className="form-label">Username</label>
                <input type="text" name="username" className="form-control" value={formData.username} onChange={handleChange} />
              </div>
              <div className="col mb-4">
                <label className="form-label">Email</label>
                <input type="email" name="email" className="form-control" value={formData.email} onChange={handleChange} />
              </div>
            </div>
          </div>

          {/* Step 2 - Username */}
          <div className={`fade-step ${step === 2 ? "show" : "hide"}`}>
            <div className="row">
              <div className="col mb-4">
                <label className="form-label">Phone</label>
                <input type="tel" ref={phoneInputRef} className="form-control" />
              </div>
              <div className="col mb-4">
                <label className="form-label">Date of Birth</label>
                <input type="date" name="date_of_birth" className="form-control" value={formData.date_of_birth} onChange={handleChange} />
              </div>
            </div>
          </div>

          {/* Step 3 - Contact & DOB */}
          <div className={`fade-step ${step === 3 ? "show" : "hide"}`}>
            <div className="row">
              <div className="col mb-4">
                <label className="form-label">Region</label>
                <input type="text" name="region" className="form-control" value={formData.region} onChange={handleChange} />
              </div>
              <div className="col mb-4">
                <label className="form-label">District (optional)</label>
                <input type="text" name="district" className="form-control" value={formData.district} onChange={handleChange} />
              </div>
            </div>
          </div>

          {/* Step 4 - District */}
          <div className={`fade-step ${step === 4 ? "show" : "hide"}`}>
            <div className="row">
              <div className="col mb-4">
                <label className="form-label">Password</label>
                <input type="password" name="password" className="form-control" value={formData.password} onChange={handleChange} />
              </div>
              <div className="col mb-4">
                <label className="form-label">Confirm Password</label>
                <input type="password" name="password2" className="form-control" value={formData.password2} onChange={handleChange} />
              </div>
            </div>
          </div>

          {/* Step 5 - Password */}
          <div className={`fade-step ${step === 5 ? "show" : "hide"}`}>
            <h3>
              YOU ARE ALMOST DONE,
              CLICK THE BUTTON, NEW USER.
            </h3>
          </div>

          <div className="d-flex justify-content-between">
            {step > 1 && <Button type="button" variant="outline-secondary" onClick={handlePrev}>Previous</Button>}
            {step < 5 ? (
              <Button type="button" onClick={handleNext}>Next</Button>
            ) : (
              <Button type="submit" className="w-50">Register</Button>
            )}
          </div>

          <div className="mt-3 text-center">
            <Link to="/login" style={{ color: "#0d6efd" }} className="text-decoration-none">
              Already have an account?
            </Link>
          </div>
        </form>
      </div>
    </>
  );
}

export default Register;

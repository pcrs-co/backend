import { ACCESS_TOKEN, REFRESH_TOKEN } from "../../utils/constants.js";
import { useNavigate, Link } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../../utils/api";
import { useState, useEffect } from "react";
import { Input, Ripple, initMDB } from "mdb-ui-kit";
import Button from "../../features/ReusableButton.jsx";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    initMDB({ Input, Ripple });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!username || !password) {
      toast.error("Username and Password are required");
      return;
    }

    try {
      const response = await api.post("/api/token/", { username, password });

      localStorage.setItem(ACCESS_TOKEN, response.data.access);
      localStorage.setItem(REFRESH_TOKEN, response.data.refresh);
      localStorage.setItem("userRole", response.data.role);
      localStorage.setItem("username", response.data.username);

      toast.success("Login successful!");

      switch (response.data.role) {
        case "admin":
          navigate("/admin/dashboard");
          break;
        case "vendor":
          navigate("/vendor/dashboard");
          break;
        default:
          navigate("/");
      }
    } catch (error) {
      console.error("Login error:", error.response?.data || error.message);
      if (!error.response) {
        toast.error("Server not reachable. Is it running?");
      } else if (error.response.status === 401) {
        toast.error("Invalid credentials!");
      } else {
        toast.error("Unexpected error occurred!");
      }
    }
  };

  return (
    <>
      <div className="container mt-3">
        <Button to="/" variant="outline-primary" className="d-inline-flex align-items-center">
          Home
        </Button>
      </div>

      <div className="container mt-5 mb-3 d-flex flex-column align-items-center w-50">
        <h2 className="mb-4">Login</h2>
        <form onSubmit={handleSubmit} className="w-100">
          {/* Username or Email input */}
          <div className="form-outline mb-4">
            <label className="form-label" htmlFor="form1Example1">
              Username or Email
            </label>
            <input
              type="text"
              id="form1Example1"
              className="form-control"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />
          </div>

          {/* Password input */}
          <div className="form-outline mb-4">
            <label className="form-label" htmlFor="form1Example2">
              Password
            </label>
            <input
              type="password"
              id="form1Example2"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          {/* 2 column layout */}
          <div className="row mb-4">
            <div className="col d-flex justify-content-center">
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="form1Example3"
                  defaultChecked
                />
                <label className="form-check-label" htmlFor="form1Example3">
                  Remember me
                </label>
              </div>
            </div>

            <div className="col text-end">
              <a href="#!" className="text-decoration-none">
                Forgot password?
              </a>
            </div>
          </div>

          {/* Submit */}
          <Button type="submit" className="w-100 mb-3">
            Login
          </Button>

          <div>
            <Link
              to="/register"
              style={{ color: "#0d6efd" }}
              className="text-decoration-none"
              onMouseOver={(e) => (e.target.style.color = "#0b5ed7")}
              onMouseOut={(e) => (e.target.style.color = "#0d6efd")}
            >
              Don’t have an account?
            </Link>
          </div>
        </form>
      </div>
    </>
  );
}

export default Login;

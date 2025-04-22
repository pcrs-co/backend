import { ACCESS_TOKEN, REFRESH_TOKEN } from "../../utils/constants.js";
// import styles from '../../styles/pages/LoginPage.module.css'
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../../utils/api";
import { useState } from "react";
import { Link } from "react-router-dom";

// The Login component handles user login
function Login() {
  // State variables to store the username and password
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // Use the useNavigate hook to get the navigate function
  const navigate = useNavigate();

  // Function to handle form submission
  const handleSubmit = async (e) => {
    // Prevent the default form submission behavior
    e.preventDefault();

    if (!username || !password) {
      toast.error("Username and Password are required");
    }

    try {
      // Make a POST request to the server to log in the user
      const response = await api.post("/api/token/", { username, password });

      // Save the access and refresh tokens in local storage
      localStorage.setItem(ACCESS_TOKEN, response.data.access);
      localStorage.setItem(REFRESH_TOKEN, response.data.refresh);

      toast.success("Login successful!");

      // Redirect the user to the home page or dashboard
      navigate("/");
    } catch (error) {
      console.error("Login error:", error.response.data);
      if (!error.response) {
        toast.error("Server not reachable. Is it running?");
      } else if (error.response.status === 401) {
        toast.error("Invalid credentials!");
      } else {
        toast.error("Unexpected error occurred!");
      }
    }
  };

  // Render the Login component
  return (
    <>
      <div
        className="container mt-3 mb-3 justify-content-center text-center w-50" /* className={styles.loginContainer} */
      >
        <h2>Login</h2>

        <form /* className={styles.loginForm} */ onSubmit={handleSubmit}>
          <input
            className="form-control"
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            className="form-control mt-3"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button className="btn btn-outline-secondary mb-3 mt-3" type="submit">
            Login
          </button>
          <div>
            <Link
              to="/register"
              style={{ color: "#0d6efd" }}
              className="text-decoration-none"
              onMouseOver={(e) => (e.target.style.color = "#0b5ed7")}
              onMouseOut={(e) => (e.target.style.color = "#0d6efd")}
            >
              Don't have an account?
            </Link>
          </div>
        </form>
      </div>
    </>
  );
}

export default Login;

import { Link } from "react-router-dom";
import { ACCESS_TOKEN } from '../utils/constants'
// import searchIcon from '../../assets/icons/icons8-search.svg'

function NavigationBar() {
  const token = localStorage.getItem(ACCESS_TOKEN);
  let authLinks;

  if (token) {
    try {
      authLinks = (
        <>
          <Link className="text-decoration-none text-light mx-2" to="/profile">
            Profile
          </Link>
          <Link className="text-decoration-none text-light mx-2" to="/logout">
            Logout
          </Link>
        </>
      );
    } catch (e) {
      console.error("Failed to parse user:", e);
      authLinks = (
        <>
          <Link className="text-decoration-none text-light mx-2" to="/register">
            Sign Up
          </Link>
          <Link className="text-decoration-none text-light mx-2" to="/login">
            Login
          </Link>
        </>
      );
    }
  } else {
    authLinks = (
      <>
        <Link className="text-decoration-none text-light mx-2" to="/register">
          Sign Up
        </Link>
        <Link className="text-decoration-none text-light mx-2" to="/login">
          Login
        </Link>
      </>
    );
  }

  return (
    <>
      <header>
        <div>
          <Link to="/">
            <h3>PCRS</h3>
          </Link>
        </div>

        <div>
          <div>{authLinks}</div>
        </div>
      </header>
    </>
  );
}

export default NavigationBar;

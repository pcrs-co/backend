import { Link } from "react-router-dom";
import styles from "../../styles/layout/NavigationBar.module.css";
import { ACCESS_TOKEN } from "../../utils/constants";
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
      <header className={styles.navigationBar}>
        <div className={styles.siteLogo}>
          <Link to="/">
            <h3>PCRS</h3>
          </Link>
        </div>

        <div className={styles.authLinks}>
          <div>{authLinks}</div>
        </div>
      </header>
    </>
  );
}

export default NavigationBar;

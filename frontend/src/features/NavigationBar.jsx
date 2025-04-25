import { Link } from "react-router-dom";
import { ACCESS_TOKEN } from '../utils/constants';
import Button from './ReusableButton';

function NavigationBar() {
  const token = localStorage.getItem(ACCESS_TOKEN);
  let authLinks;

  if (token) {
    try {
      authLinks = (
        <>
          <Button to="/profile" variant="outline-light" className="mx-1">
            Profile
          </Button>
          <Button variant="danger" className="mx-1" logout>
            Logout
          </Button>
        </>
      );
    } catch (e) {
      console.error("Failed to parse user:", e);
      authLinks = (
        <>
          <Button to="/register" variant="outline-light" className="mx-1">
            Register
          </Button>
          <Button to="/login" variant="primary" className="mx-1">
            Login
          </Button>
        </>
      );
    }
  } else {
    authLinks = (
      <>
        <Button to="/register" variant="outline-light" className="mx-1">
          Register
        </Button>
        <Button to="/login" variant="primary" className="mx-1">
          Login
        </Button>
      </>
    );
  }

  return (
    <>
      <header className="d-flex justify-content-between align-items-center bg-dark text-light p-3 shadow-sm">
        <div>
          <Link
            to="/"
            className="text-decoration-none d-flex align-items-center"
          >
            <h3 className="mb-0">PCRS</h3>
          </Link>
        </div>

        <div className="d-flex gap-2 align-items-center">
          {authLinks}
        </div>
      </header>

      <style jsx>{`
        header {
          background: linear-gradient(135deg, #4e5d6c, #283034);
          border-bottom: 1px solid #444;
        }

        h3 {
          font-family: "Roboto", sans-serif;
          font-weight: bold;
          color: #ffffff;
        }

        @media (max-width: 768px) {
          header {
            flex-direction: column;
            align-items: flex-start;
          }

          .d-flex {
            flex-direction: column;
            gap: 1rem;
          }
        }
      `}</style>
    </>
  );
}

export default NavigationBar;

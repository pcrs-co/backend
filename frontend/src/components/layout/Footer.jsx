function Footer() {
  return (
    <>
      <footer className="footer">
        <div className="footer-content">
          <p>Copyright &copy; 2023 PCRS</p>
        </div>
      </footer>

      <style jsx>{`
        .footer {
          /* background-color: #2c3e50;
          color: #ecf0f1; */
          padding: 20px 0;
          text-align: center;
          font-size: 0.9rem;
        }

        .footer-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
        }

        .footer p {
          margin: 0;
          font-family: "Arial", sans-serif;
        }

        .footer-links {
          margin-top: 10px;
        }

        .footer-link {
          color: #ecf0f1;
          text-decoration: none;
          margin: 0 15px;
          font-weight: 600;
          transition: color 0.3s ease;
        }

        .footer-link:hover {
          color: #3498db;
        }

        .footer-link:active {
          color: #2980b9;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .footer-content {
            padding: 0 10px;
          }

          .footer-links {
            margin-top: 15px;
            display: flex;
            flex-direction: column;
            gap: 8px;
          }

          .footer-link {
            margin: 0;
          }
        }
      `}</style>
    </>
  );
}

export default Footer;

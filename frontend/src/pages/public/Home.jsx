import homepagePhoto from '../../assets/homepage.jpg'

function Home() {
  return (
    <>
      <div className="home-container">
        <div className="text-content">
          <h1 className="headline">
            Choose Purpose<br/>
            Get Specifications<br/>
            See Available Devices
          </h1>
          <p className="description">
            We provide device specifications, pricing, and availability to help
            you find the right device as per your needs and budget.
          </p>
          <button className="cta-button">Get Started</button>
        </div>

        <div className="image-content">
          <img src={homepagePhoto} alt="Description" className="homepage-image" />
        </div>
      </div>

      <style jsx>{`
        .home-container {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 30px 10%;
          border-radius: 12px;
        }

        .text-content {
          max-width: 600px;
          padding-right: 20px;
        }

        .headline {
          font-family: "Roboto", sans-serif;
          font-size: 3rem;
          font-weight: 700;
          background: linear-gradient(to right, #2c3e50, #34495e); /* New gradient */
          -webkit-background-clip: text;
          color: transparent;
          margin-bottom: 1rem;
          line-height: 1.2;
        }

        .description {
          font-family: "Arial", sans-serif;
          font-size: 1.2rem;
          color: #333; /* Dark color for description text */
          margin-bottom: 1.5rem;
          line-height: 1.6;
        }

        .cta-button {
          padding: 12px 25px;
          background-color: #2980b9;
          color: white;
          border: none;
          font-size: 1.1rem;
          font-weight: 600;
          border-radius: 5px;
          cursor: pointer;
          transition: background-color 0.3s ease, transform 0.2s ease;
        }

        .cta-button:hover {
          background-color: #2471a3;
          transform: scale(1.05);
        }

        .cta-button:active {
          background-color: #1f618d;
        }

        /* Image styles */
        .homepage-image {
          max-height: 400px; /* Limit height */
          object-fit: cover; /* Ensures the image doesn't stretch */
          border-radius: 12px; /* Rounded corners */
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* Optional: add some shadow */
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .home-container {
            flex-direction: column;
            align-items: flex-start;
            padding: 40px 5%;
          }

          .headline {
            font-size: 2rem;
          }

          .description {
            font-size: 1rem;
          }

          /* For small screens, you might want to adjust the image size */
          .homepage-image {
            max-height: 300px; /* Smaller size for smaller screens */
          }
        }
      `}</style>
    </>
  );
}

export default Home;

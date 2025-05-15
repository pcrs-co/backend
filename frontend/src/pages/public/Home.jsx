import homepagePhoto from '../../assets/homepage.jpg';
import Button from '../../features/ReusableButton'; // Adjust the path if needed

function Home() {
  return (
    <>
      <div className="home-container">
        <div className="text-content">
          <h1 className="headline">
            Choose Purpose<br />
            Get Specifications<br />
            See Available Devices
          </h1>
          <p className="description">
            We provide device specifications, pricing, and availability to help
            you find the right device as per your needs and budget.
          </p>
          <Button to="/input-basic" variant="primary" size="lg" className="cta-button">
            Get Started
          </Button>
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
          background: linear-gradient(to right, #2c3e50, #34495e);
          -webkit-background-clip: text;
          color: transparent;
          margin-bottom: 1rem;
          line-height: 1.2;
        }

        .description {
          font-family: "Arial", sans-serif;
          font-size: 1.2rem;
          color: #333;
          margin-bottom: 1.5rem;
          line-height: 1.6;
        }

        .cta-button {
          font-weight: 600;
          padding: 12px 25px;
          border-radius: 5px;
        }

        .homepage-image {
          max-height: 400px;
          object-fit: cover;
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

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

          .homepage-image {
            max-height: 300px;
          }
        }
      `}</style>
    </>
  );
}

export default Home;

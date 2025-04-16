import ApproachSelection from "../features/ApproachSelection.jsx";
import gearIcon from "../../assets/icons/icons8-gear-100.svg";
import styles from "../../styles/pages/HomePage.module.css";

function Home() {
  return (
    <>
      <div className={styles.intro}>
        <div className={styles.introHero}>
          <h1>
            Choose Purpose. Get Specs.
            <br />
            See Available Devices.
          </h1>
          <p>
            We provide device specifications, pricing, and availability to help
            you find the right device as per your needs and budget.
          </p>
          <button>
            <img src={gearIcon} className={styles.gearIcon} /> Get Started{" "}
          </button>
        </div>

        <div className={styles.approachSelectionContainer}>
          <ApproachSelection />
        </div>
      </div>
    </>
  );
}

export default Home;

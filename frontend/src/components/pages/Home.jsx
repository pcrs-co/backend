import NavigationBar from '../layout/NavigationBar.jsx'
import styles from '../../styles/pages/Home.module.css'

function Home() {

  return (
    <>
      <NavigationBar />

      <div className={styles.intro}>
        <h1>Your Perfect Laptop Awaits</h1>
        <p>Compare Specs, Find Your Ideal Match.</p>
      </div>

    </>
  )
}

export default Home

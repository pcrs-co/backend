import { Link } from 'react-router-dom'
import styles from '../../styles/layout/NavigationBar.module.css'
// import searchIcon from '../../assets/icons/icons8-search.svg'


function NavigationBar() {

    return (
        <>
            <header className={styles.navigationBar}>

                <div className={styles.siteLogo}>
                    <a href="/home">
                    <h3>PCRS</h3>
                    </a>
                </div>

                <div className={styles.authLinks}>
                    <div className={styles.searchBar}>
                        <input 
                            type="text" 
                            placeholder="Search" 
                            style={{ 
                                backgroundColor: 'transparent',
                                border: 'none',
                                outline: 'none',
                                color: 'white'
                            }} 
                        />
                        {/* <button>
                            <img src={searchIcon} className={styles.searchIcon}/>
                        </button> */}
                    </div>
                    <Link to="/register">Sign Up</Link> | 
                    <Link to="/login">Login</Link>                 
                </div>
                
            </header>
        </>
    )
}

export default NavigationBar
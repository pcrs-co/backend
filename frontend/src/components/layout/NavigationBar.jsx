import styles from '../../styles/layout/NavigationBar.module.css'
import searchIcon from '../../assets/icons/icons8-search.svg'

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
                    <a href="/register">Sign Up</a> | 
                    <a href="/login">Login</a>                 
                </div>
                
            </header>
        </>
    )
}

export default NavigationBar
import styles from '../../styles/layout/NavigationBar.module.css'

function NavigationBar() {

    return (
        <>
            <header className={styles.navigationBar}>

                <div className={styles.siteLogo}>
                    <a href="/home">
                    <h3>PCRS</h3>
                    </a>
                </div>

                {/* <div className={styles.searchBar}>
                    <input 
                        type="text" 
                        placeholder="Search" 
                        style={{ 
                            backgroundColor: 'transparent',
                            border: 'none'
                         }} 
                    />
                </div> */}

                <div className={styles.authLinks}>
                    <a href="/register">Sign Up</a> | 
                    <a href="/login">Login</a>                 
                </div>
                
            </header>
        </>
    )
}

export default NavigationBar
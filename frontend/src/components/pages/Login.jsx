import Header from '../layout/Header.jsx'
import styles from '../../styles/pages/LoginPage.module.css'
import Footer from '../layout/Footer.jsx'

function Login() {

    return (
        <>
            <Header />

            <div className={styles.loginContainer}>
                <h1>Login</h1>
                    
                    <form className={styles.loginForm}>
                        <input 
                            type="text" 
                            placeholder="Username" 
                        />
                        <input 
                            type="password" 
                            placeholder="Password" 
                        />
                        <button type="submit">
                            Login
                        </button>  
                    </form>

            </div>

            <Footer />
        </>
    )
}

export default Login

import Header from '../layout/Header.jsx'
import styles from '../../styles/pages/RegisterPage.module.css'
import Footer from '../layout/Footer.jsx'

function Register() {

    return (
        <>
            <Header />

            <div className={styles.registerContainer}>
                <h1>Register</h1>
                    
                    <form className={styles.registerForm}>
                        <input 
                            type="text" 
                            placeholder="Username" 
                        />
                        <input 
                            type="email" 
                            placeholder="Email" 
                        />
                        <input
                            type="tel"
                            placeholder="Phone Number"
                        />
                        <input
                            type="date"
                            placeholder="Date Of Birth"
                        />
                        <input
                            type="text"
                            placeholder="Region"
                        />
                        <input 
                            type="password" 
                            placeholder="Password" 
                        />
                        <input 
                            type="password" 
                            placeholder="Confirm Password" 
                        />
                        <button type="submit">
                            Register
                        </button>  
                    </form>

            </div>

            <Footer />
        </>
    )
}

export default Register

function NavigationBar() {

    return (
        <>
            <header>
                <span className="site-logo">
                <h1>PCRS</h1>
                {/* <div>
                    <input 
                        type="text" 
                        placeholder="Search" 
                        style={{ 
                            backgroundColor: 'transparent',
                            border: 'none'
                         }} 
                    />
                </div> */}
                </span>
                <span className="auth-links">
                    <a href="/register">Register</a> | 
                    <a href="/login">Login</a>                 
                </span>
            </header>
        </>
    )
}

export default NavigationBar
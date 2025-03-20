function NavigationBar() {

    return (
        <>
            <header className="navigation-bar">
                <div className="site-logo">
                    <h1>PCRS</h1>
                </div>
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
                <div className="auth-links">
                    <a href="/register">Register</a> | 
                    <a href="/login">Login</a>                 
                </div>
            </header>
        </>
    )
}

export default NavigationBar
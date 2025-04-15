import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'

function AppToastContainer() {
    return (
        <ToastContainer
            position="top-center"
            autoClose={3000}
            hideProgressBar={false}
            newestOnTop={true}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="colored"
        />
    )
}

export default AppToastContainer
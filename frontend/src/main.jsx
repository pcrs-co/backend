import 'intl-tel-input/build/css/intlTelInput.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import { createRoot } from 'react-dom/client'
import { StrictMode } from 'react'
import './styles/reset.css'
import './styles/theme.css'
import './styles/type.css'
import './styles/phone.css'
import App from './App'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)


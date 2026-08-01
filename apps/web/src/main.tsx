import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './i18n'
import './styles.css'
import { App } from './App'
import { ErrorBoundary } from './components/ErrorBoundary'
import { LanguageProvider } from './contexts/LanguageContext'

createRoot(document.getElementById('root')!).render(<StrictMode><ErrorBoundary><LanguageProvider><App/></LanguageProvider></ErrorBoundary></StrictMode>)

import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import ar from './locales/ar.json'
import fr from './locales/fr.json'

export const DEFAULT_LANGUAGE = 'fr'
export type AppLanguage = 'fr' | 'ar'

const storedLanguage = typeof window !== 'undefined' ? window.localStorage.getItem('meip-language') : null
const initialLanguage: AppLanguage = storedLanguage === 'ar' ? 'ar' : DEFAULT_LANGUAGE

void i18n.use(initReactI18next).init({
  resources: { ar: { translation: ar }, fr: { translation: fr } },
  lng: initialLanguage,
  fallbackLng: DEFAULT_LANGUAGE,
  interpolation: { escapeValue: false },
  returnNull: false,
})

export default i18n

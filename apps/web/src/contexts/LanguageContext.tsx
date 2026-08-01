import { createContext, type PropsWithChildren, useCallback, useContext, useEffect, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import type { AppLanguage } from '../i18n'

type LanguageContextValue = { language: AppLanguage; direction: 'ltr' | 'rtl'; setLanguage: (language: AppLanguage) => void; toggleLanguage: () => void }
const LanguageContext = createContext<LanguageContextValue | null>(null)

export function LanguageProvider({ children }: PropsWithChildren) {
  const { i18n } = useTranslation()
  const language: AppLanguage = i18n.language.startsWith('ar') ? 'ar' : 'fr'
  const direction: 'ltr' | 'rtl' = language === 'ar' ? 'rtl' : 'ltr'
  const setLanguage = useCallback((next: AppLanguage) => { window.localStorage.setItem('meip-language', next); void i18n.changeLanguage(next) }, [i18n])
  const toggleLanguage = useCallback(() => setLanguage(language === 'ar' ? 'fr' : 'ar'), [language, setLanguage])
  useEffect(() => { document.documentElement.lang = language; document.documentElement.dir = direction }, [direction, language])
  const value = useMemo(() => ({ language, direction, setLanguage, toggleLanguage }), [direction, language, setLanguage, toggleLanguage])
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (!context) throw new Error('useLanguage must be used within LanguageProvider')
  return context
}

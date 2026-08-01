import { Languages } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useLanguage } from '../contexts/LanguageContext'

export function LanguageSwitcher() {
  const { t } = useTranslation()
  const { toggleLanguage } = useLanguage()
  return <button type="button" onClick={toggleLanguage} aria-label={`${t('language.label')}: ${t('language.switchTo')}`} className="inline-flex min-h-11 min-w-11 items-center justify-center gap-2 rounded-full border border-slate-200 bg-white px-2 text-sm font-semibold text-slate-700 transition hover:border-mauritania-500 hover:text-mauritania-700 focus:outline-none focus:ring-2 focus:ring-mauritania-500 focus:ring-offset-2 sm:px-3.5"><Languages size={16} aria-hidden="true" /><span className="hidden min-[360px]:inline">{t('language.switchTo')}</span></button>
}

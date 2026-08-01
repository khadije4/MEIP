import { ArrowLeft, Construction } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link, useLocation } from 'react-router-dom'

export function FeaturePlaceholder() {
  const { t } = useTranslation(); const location = useLocation(); const key = location.pathname.slice(1) || 'overview'
  return <main className="mx-auto grid min-h-[68vh] max-w-7xl place-items-center px-4 py-16 sm:px-6 lg:px-8"><section className="max-w-xl text-center"><span className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-gold-400/15 text-gold-500"><Construction size={26}/></span><p className="mt-5 text-xs font-bold uppercase tracking-[0.2em] text-mauritania-700">{t('placeholder.badge')}</p><h1 className="mt-3 text-3xl font-black tracking-tight text-slate-950">{t(`nav.${key}`, { defaultValue: t('placeholder.title') })}</h1><p className="mt-4 leading-7 text-slate-600">{t('placeholder.description')}</p><Link to="/" className="mt-7 inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-5 py-3 font-bold text-slate-700 hover:border-mauritania-500 hover:text-mauritania-700"><ArrowLeft size={17}/>{t('placeholder.back')}</Link></section></main>
}

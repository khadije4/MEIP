import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
export function NotFound() { const { t } = useTranslation(); return <main className="grid min-h-[68vh] place-items-center px-6 text-center"><section><p className="text-7xl font-black text-mauritania-100">404</p><h1 className="mt-2 text-3xl font-black text-slate-950">{t('notFound.title')}</h1><p className="mt-3 text-slate-600">{t('notFound.description')}</p><Link to="/" className="mt-6 inline-block rounded-full bg-mauritania-700 px-5 py-3 font-bold text-white">{t('notFound.back')}</Link></section></main> }

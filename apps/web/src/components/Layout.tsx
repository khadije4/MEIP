import { Menu, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { NavLink, Outlet } from 'react-router-dom'
import { LanguageSwitcher } from './LanguageSwitcher'

const navigation = [
  ['home', '/'], ['overview', '/dashboard'], ['compare', '/explore?tab=compare'], ['stress', '/simulate'], ['assistant', '/assistant'],
] as const

export function Layout() {
  const { t } = useTranslation(); const [open, setOpen] = useState(false)
  useEffect(()=>{document.body.style.overflow=open?'hidden':'';return()=>{document.body.style.overflow=''}},[open])
  return <div className="flex min-h-screen flex-col bg-[#f7f9f8] text-slate-900">
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/95 backdrop-blur"><div className="mx-auto flex h-18 max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
      <NavLink to="/" className="flex items-center gap-3" onClick={() => setOpen(false)}><span className="grid h-10 w-10 place-items-center rounded-xl bg-mauritania-700 font-black tracking-tight text-white shadow-lg shadow-mauritania-700/20">M</span><span><strong className="block text-sm leading-tight text-mauritania-900">{t('brand.name')}</strong><span className="hidden max-w-52 text-[11px] leading-tight text-slate-500 sm:block">{t('brand.fullName')}</span></span></NavLink>
      <nav className="hidden items-center gap-1 xl:flex" aria-label={t('nav.menu')}>{navigation.map(([key,path]) => <NavLink key={key} to={path} className={({isActive}) => `rounded-full px-4 py-2 text-sm font-bold transition focus:outline-none focus:ring-2 focus:ring-mauritania-400 ${key==='stress' ? (isActive?'bg-gold-400 text-navy-950 shadow-sm':'bg-mauritania-700 text-white hover:bg-mauritania-600') : (isActive?'bg-mauritania-50 text-mauritania-700':'text-slate-600 hover:bg-slate-50 hover:text-slate-950')}`}>{t(`nav.${key}`)}</NavLink>)}</nav>
      <div className="flex items-center gap-2"><LanguageSwitcher/><button className="grid h-11 w-11 place-items-center rounded-full border border-slate-200 xl:hidden" type="button" onClick={() => setOpen(!open)} aria-label={t(open ? 'nav.close' : 'nav.menu')} aria-expanded={open}>{open ? <X size={19}/> : <Menu size={19}/>}</button></div>
    </div>{open && <nav className="border-t border-slate-100 bg-white px-4 py-4 xl:hidden" aria-label={t('nav.menu')}><div className="mx-auto grid max-w-7xl grid-cols-2 gap-2 sm:grid-cols-3">{navigation.map(([key,path]) => <NavLink key={key} to={path} onClick={() => setOpen(false)} className={({isActive}) => `min-h-11 rounded-xl px-3 py-3 text-sm font-bold focus:ring-2 ${key==='stress'?'bg-mauritania-700 text-white':isActive?'bg-mauritania-50 text-mauritania-700':'text-slate-600 hover:bg-slate-50'}`}>{t(`nav.${key}`)}</NavLink>)}</div></nav>}</header>
    <div className="flex-1"><Outlet/></div>
    <footer className="border-t border-slate-200 bg-white"><div className="mx-auto flex max-w-7xl flex-col gap-2 px-4 py-7 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8"><span>{t('footer.source')}</span><span>{t('footer.disclaimer')}</span></div></footer>
  </div>
}

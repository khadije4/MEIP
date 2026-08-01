import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { Layout } from '../components/Layout'
import { LanguageProvider } from '../contexts/LanguageContext'
import { FeaturePlaceholder } from '../pages/FeaturePlaceholder'
import { Home } from '../pages/Home'

function renderRoute(path = '/') {
  return render(<LanguageProvider><MemoryRouter initialEntries={[path]}><Routes><Route path="/" element={<Layout/>}><Route index element={<Home/>}/><Route path="overview" element={<FeaturePlaceholder/>}/></Route></Routes></MemoryRouter></LanguageProvider>)
}

describe('Phase 4 frontend foundation', () => {
  it('renders the French home page, source, period, and current-price limitation', () => {
    renderRoute()
    expect(screen.getByRole('heading', { level: 1, name: /Comprendre l’économie mauritanienne/i })).toBeInTheDocument()
    expect(screen.getByText(/ANSADE\/CN — tableaux 4\.9\.1 et 4\.9\.2/)).toBeInTheDocument()
    expect(screen.getByText(/27 observations annuelles/)).toBeInTheDocument()
    expect(screen.getByText(/ne mesurent ni la croissance réelle ni l’inflation/i)).toBeInTheDocument()
  })

  it('switches to Arabic and applies RTL to the document', async () => {
    const user = userEvent.setup(); renderRoute()
    await user.click(screen.getByRole('button', { name: /العربية/ }))
    expect(await screen.findByRole('heading', { level: 1, name: /فهم الاقتصاد الموريتاني/ })).toBeInTheDocument()
    expect(document.documentElement).toHaveAttribute('lang', 'ar')
    expect(document.documentElement).toHaveAttribute('dir', 'rtl')
    expect(window.localStorage.getItem('meip-language')).toBe('ar')
  })

  it('keeps Phase 5 destinations explicit without presenting fake analytics', () => {
    renderRoute('/overview')
    expect(screen.getByRole('heading', { level: 1, name: 'Économie' })).toBeInTheDocument()
    expect(screen.getByText(/visualisations et interactions.*Phase 5/i)).toBeInTheDocument()
  })
})

import { Component, type ErrorInfo, type ReactNode } from 'react'
import i18n from '../i18n'

type State = { hasError: boolean }
export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { hasError: false }
  static getDerivedStateFromError(): State { return { hasError: true } }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error('MEIP render error', error, info) }
  render() {
    if (!this.state.hasError) return this.props.children
    return <main className="grid min-h-screen place-items-center bg-slate-50 p-6"><section className="max-w-lg rounded-3xl border border-red-100 bg-white p-8 text-center shadow-card"><p className="text-xs font-bold uppercase tracking-[0.18em] text-red-600">MEIP</p><h1 className="mt-3 text-2xl font-bold text-slate-950">{i18n.t('error.title')}</h1><p className="mt-3 text-slate-600">{i18n.t('error.description')}</p><button type="button" onClick={() => window.location.reload()} className="mt-6 rounded-full bg-mauritania-700 px-5 py-2.5 font-semibold text-white">{i18n.t('error.retry')}</button></section></main>
  }
}

import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'

export function PageHeader({ eyebrow, title, description, actions }: { eyebrow: string; title: string; description: string; actions?: ReactNode }) {
  return <header className="flex flex-col gap-5 border-b border-slate-200 pb-7 lg:flex-row lg:items-end lg:justify-between"><div className="max-w-3xl"><p className="text-xs font-bold uppercase tracking-[0.18em] text-mauritania-700">{eyebrow}</p><h1 className="mt-2 text-3xl font-black tracking-tight text-slate-950 sm:text-4xl">{title}</h1><p className="mt-3 leading-7 text-slate-600">{description}</p></div>{actions && <div className="shrink-0">{actions}</div>}</header>
}

export function KpiCard({ label, value, note, icon: Icon }: { label: string; value: string; note?: string; icon?: LucideIcon }) {
  return <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card"><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-medium text-slate-500">{label}</p><p className="mt-2 text-2xl font-black tracking-tight text-slate-950">{value}</p>{note && <p className="mt-1.5 text-xs text-slate-500">{note}</p>}</div>{Icon && <span className="grid h-10 w-10 place-items-center rounded-xl bg-mauritania-50 text-mauritania-700"><Icon size={19}/></span>}</div></article>
}

export function Panel({ title, subtitle, children, className = '' }: { title: string; subtitle?: string; children: ReactNode; className?: string }) {
  return <section className={`rounded-3xl border border-slate-200 bg-white p-5 shadow-card sm:p-6 ${className}`}><div className="mb-5"><h2 className="text-lg font-bold text-slate-950">{title}</h2>{subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}</div>{children}</section>
}

export function StatePanel({ state, title, description }: { state: 'loading' | 'error' | 'empty'; title: string; description: string }) {
  return <div role={state === 'error' ? 'alert' : 'status'} className={`rounded-2xl border p-7 text-center ${state === 'error' ? 'border-red-200 bg-red-50' : 'border-slate-200 bg-white'}`}><div className={`mx-auto h-2 w-16 rounded-full ${state === 'loading' ? 'animate-pulse bg-mauritania-500' : state === 'error' ? 'bg-red-500' : 'bg-slate-300'}`}/><h2 className="mt-4 font-bold text-slate-950">{title}</h2><p className="mt-1 text-sm text-slate-600">{description}</p></div>
}

export function WarningBanner({ title, children }: { title: string; children: ReactNode }) {
  return <aside className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-amber-950"><p className="font-bold">{title}</p><div className="mt-1 text-sm leading-6 text-amber-900/80">{children}</div></aside>
}

export function PageContainer({ children }: { children: ReactNode }) { return <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">{children}</main> }

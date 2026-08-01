import type { ReactNode } from 'react'
import { useLanguage } from '../contexts/LanguageContext'

// Shared localization hook intentionally lives beside the display primitives that consume it.
// eslint-disable-next-line react-refresh/only-export-components
export function useCopy() {
  const { language } = useLanguage()
  return (fr: string, ar: string) => language === 'ar' ? ar : fr
}

export function NumberValue({ value, percent = false }: { value: number | null | undefined; percent?: boolean }) {
  const { language } = useLanguage()
  if (value == null) return <MissingValue/>
  return <>{new Intl.NumberFormat(language === 'ar' ? 'ar-MR' : 'fr-MR', { maximumFractionDigits: 2 }).format(value)}{percent ? ' %' : ''}</>
}

export function MissingValue() { const c=useCopy(); return <span className="text-slate-400" title={c('Valeur non disponible','القيمة غير متاحة')}>—</span> }

export function Metadata({ source='ANSADE/CN', unit='Millions de MRU' }: { source?: string; unit?: string }) {
  const c=useCopy(); return <div className="mt-4 flex flex-wrap gap-2 text-xs"><span className="rounded-full bg-mauritania-50 px-3 py-1 font-semibold text-mauritania-800">{c('Source','المصدر')}: {source}</span><span className="rounded-full bg-slate-100 px-3 py-1 text-slate-600">{c('Unité','الوحدة')}: {unit}</span></div>
}

export function CurrentPriceWarning() { const c=useCopy(); return <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"><strong>{c('Prix courants : ','الأسعار الجارية: ')}</strong>{c('les variations sont nominales et ne mesurent pas la croissance réelle.','التغيرات اسمية ولا تقيس النمو الحقيقي.')}</div> }

export function SelectField({ label, value, onChange, children, testId }: { label:string; value:string|number; onChange:(value:string)=>void; children:ReactNode; testId?:string }) {
  return <label className="grid min-w-0 gap-1 text-sm font-semibold text-slate-700"><span>{label}</span><select data-testid={testId} className="min-h-11 min-w-0 w-full max-w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 font-normal" value={value} onChange={event=>onChange(event.target.value)}>{children}</select></label>
}

export function DataTable({ headers, rows }: { headers:string[]; rows:ReactNode[][] }) {
  return <div className="overflow-x-auto"><table className="w-full min-w-[620px] text-sm"><thead><tr className="border-b border-slate-200 text-start text-slate-500">{headers.map(h=><th className="px-3 py-3 text-start" key={h}>{h}</th>)}</tr></thead><tbody>{rows.map((row,i)=><tr className="border-b border-slate-100" key={i}>{row.map((cell,j)=><td className="px-3 py-3" key={j}>{cell}</td>)}</tr>)}</tbody></table></div>
}

export function Badge({ children, tone='neutral' }: {children:ReactNode; tone?:'neutral'|'warning'|'danger'|'good'}) {
  const classes={neutral:'bg-slate-100 text-slate-700',warning:'bg-amber-100 text-amber-900',danger:'bg-red-100 text-red-800',good:'bg-emerald-100 text-emerald-800'}
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${classes[tone]}`}>{children}</span>
}

export function DownloadCsv({ filename, headers, rows }: {filename:string;headers:string[];rows:Array<Array<string|number|null>>}) {
  const c=useCopy(); const download=()=>{ const csv=[headers,...rows].map(row=>row.map(value=>`"${String(value??'').replaceAll('"','""')}"`).join(',')).join('\n'); const url=URL.createObjectURL(new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8'})); const a=document.createElement('a');a.href=url;a.download=filename;a.click();URL.revokeObjectURL(url) }
  return <button type="button" onClick={download} className="rounded-xl bg-mauritania-700 px-4 py-2.5 text-sm font-bold text-white">{c('Télécharger CSV','تنزيل CSV')}</button>
}

import { useTranslation } from 'react-i18next'
import { useLanguage } from '../contexts/LanguageContext'
import { useApi } from '../hooks/useApi'
import type { Indicator } from '../types/economic'
import { indicatorName } from '../utils/format'

export function IndicatorSelect({ value, onChange, label, sourceSide }: { value: string; onChange: (value: string) => void; label: string; sourceSide?: string }) {
  const { language } = useLanguage(); const { t } = useTranslation(); const { data, loading } = useApi<Indicator[]>('/api/indicators')
  const options = (data ?? []).filter((i) => !i.is_alias && (!sourceSide || i.source_side === sourceSide))
  return <label className="block text-sm font-semibold text-slate-700"><span>{label}</span><select disabled={loading} value={value} onChange={(e) => onChange(e.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm focus:border-mauritania-500 focus:outline-none focus:ring-2 focus:ring-mauritania-100"><option value="">{loading ? t('states.loading') : t('forms.selectIndicator')}</option>{options.map((item) => <option key={item.code} value={item.code}>{indicatorName(item,language)}</option>)}</select></label>
}

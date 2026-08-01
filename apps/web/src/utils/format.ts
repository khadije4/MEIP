export function formatNumber(value: number | null | undefined, language: string, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return language === 'ar' ? 'غير متاح' : 'Non disponible'
  return new Intl.NumberFormat(language === 'ar' ? 'ar-MR' : 'fr-FR', { maximumFractionDigits: digits, minimumFractionDigits: digits }).format(value)
}

export function indicatorName(item: { name_fr: string; name_ar?: string | null }, language: string) {
  return language === 'ar' && item.name_ar ? item.name_ar : item.name_fr
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = filename; link.click(); URL.revokeObjectURL(url)
}

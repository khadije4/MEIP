import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { LanguageProvider, useLanguage } from '../contexts/LanguageContext'
import { AssistantExperiencePage } from '../pages/AssistantExperiencePage'
import { ResponseTimeline } from '../components/recommendations/ResponseTimeline'
import type { Recommendation } from '../types/economic'

const item: Recommendation = {
  code:'secondary_sector_immediate_v1', title_fr:'Maintenir les opérations essentielles', title_ar:'الحفاظ على العمليات الأساسية', description_fr:'Action', description_ar:'إجراء',
  time_horizon:'immediate', priority:'critical', sector_codes:['secondary_sector'], reason_fr:'Raison observée.', reason_ar:'سبب مرصود.',
  supporting_metrics:[{label_fr:'Impact direct sur le PIB',label_ar:'الأثر المباشر على الناتج',value:12,unit:'%'}],
  responsible_actor_categories:['public_authorities'], implementation_steps_fr:['Vérifier les besoins.'], implementation_steps_ar:['التحقق من الاحتياجات.'],
  monitoring_indicators:['secondary_sector','gdp_activity_market_prices'], escalation_trigger_fr:'Escalader si nécessaire.', escalation_trigger_ar:'التصعيد عند الحاجة.',
  expected_objective_fr:'Maintenir la continuité.', expected_objective_ar:'الحفاظ على الاستمرارية.', confidence:'moderate',
  confidence_reason_fr:'Données d’entreprise indisponibles.', confidence_reason_ar:'بيانات المؤسسات غير متاحة.', limitations_fr:'À valider.', limitations_ar:'يتطلب التحقق.',
}
function LanguageToggle(){const {toggleLanguage}=useLanguage();return <button onClick={toggleLanguage}>العربية</button>}

it('serves the Assistant component on direct /assistant navigation', () => {
  render(<LanguageProvider><MemoryRouter initialEntries={['/assistant']}><Routes><Route path="assistant" element={<AssistantExperiencePage/>}/></Routes></MemoryRouter></LanguageProvider>)
  expect(screen.getByRole('heading',{level:1,name:'Assistant économique'})).toBeInTheDocument()
  expect(screen.getByRole('button',{name:'Interroger'})).toBeInTheDocument()
})

it('localizes recommendation metadata and keeps raw codes inside technical details', async () => {
  const user=userEvent.setup(); render(<LanguageProvider><LanguageToggle/><ResponseTimeline recommendations={[item]}/></LanguageProvider>)
  expect(screen.getByText('Critique')).toBeInTheDocument()
  expect(screen.getByText((_,element)=>element?.tagName==='CODE'&&element.textContent?.includes('secondary_sector')===true)).not.toBeVisible()
  await user.click(screen.getByRole('button',{name:'العربية'}))
  expect(screen.getByText('حرجة')).toBeInTheDocument()
  expect(screen.getByText('الحفاظ على العمليات الأساسية')).toBeInTheDocument()
})

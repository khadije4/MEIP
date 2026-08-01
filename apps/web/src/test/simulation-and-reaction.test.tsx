import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LanguageProvider } from '../contexts/LanguageContext'
import { SimulationAndReactionPage } from '../pages/SimulationAndReactionPage'
import * as stress from '../services/stressTest'
import * as recommendations from '../services/recommendations'
import i18n from '../i18n'

vi.mock('../services/stressTest')
vi.mock('../services/recommendations')

const sectors=[
  {id:3,code:'primary_sector',name_fr:'Secteur primaire',name_ar:'القطاع الأولي',category:'sector',hierarchy_level:1,unit:'Millions de MRU',source_side:'activity',is_aggregate:false,is_alias:false},
  {id:1,code:'extractive_activities',name_fr:'Activités extractives',name_ar:'الأنشطة الاستخراجية',category:'subsector',hierarchy_level:2,unit:'Millions de MRU',source_side:'activity',is_aggregate:false,is_alias:false},
  {id:2,code:'fishing',name_fr:'Pêche',name_ar:'الصيد البحري',category:'subsector',hierarchy_level:3,unit:'Millions de MRU',source_side:'activity',is_aggregate:false,is_alias:false},
]
const composition=[2023,2024].map(year=>({year,gdp:400,primary_sector:80,extractive_activities:70,manufacturing:40,construction_public_works:30,tertiary_sector:180}))
const simulation={year:2024,baseline_activity_gdp:400,indicator_code:'extractive_activities',name_fr:'Activités extractives',name_ar:'الأنشطة الاستخراجية',sector_value:80,sector_share_of_gdp_pct:20,shock_rate:.5,direct_loss:40,simulated_gdp:360,direct_gdp_impact_pct:10,current_price_warning_fr:'Prix courants',current_price_warning_ar:'أسعار جارية',methodology_disclaimer_fr:'Direct uniquement',methodology_disclaimer_ar:'مباشر فقط',source:'ANSADE/CN',unit:'Millions de MRU'}
const recommendation={code:'extractive_immediate',title_fr:'Préserver les infrastructures',title_ar:'حماية البنية التحتية',description_fr:'Action',description_ar:'إجراء',time_horizon:'immediate',priority:'critical',sector_codes:['extractive_activities'],reason_fr:'Le choc est important.',reason_ar:'الصدمة كبيرة.',supporting_metrics:[],monitoring_indicators:['exports'],expected_objective_fr:'Continuité',expected_objective_ar:'الاستمرارية',confidence:'high',limitations_fr:'À valider.',limitations_ar:'يتطلب التحقق.'}

function setupMocks() {
  vi.mocked(stress.loadSimulationPageData).mockResolvedValue({sectors,years:[2023,2024],composition})
  vi.mocked(stress.loadImpactPreview).mockResolvedValue({sectorValue:80,baselineGdp:400})
  vi.mocked(stress.simulateSingle).mockResolvedValue(simulation)
  vi.mocked(stress.loadDependency).mockResolvedValue({indicator_code:'extractive_activities',points:[{year:2023,dependency_pct:18},{year:2024,dependency_pct:20}],minimum_dependency_pct:18,maximum_dependency_pct:20,latest_dependency_pct:20,average_dependency_pct:19,source:'ANSADE/CN',unit:'Millions de MRU'})
  vi.mocked(recommendations.generateRecommendations).mockResolvedValue({year:2024,risk_level:'critical',risk_basis_fr:'Risque direct.',risk_basis_ar:'مخاطر مباشرة.',stress_test:{} as never,recommendations:[recommendation],alternative_sectors:[],monitoring_indicators:['exports'],disclaimer_fr:'Options non officielles.',disclaimer_ar:'خيارات غير رسمية.',source:'ANSADE/CN',unit:'Millions de MRU'})
}
function renderPage(){return render(<LanguageProvider><SimulationAndReactionPage/></LanguageProvider>)}

describe('SimulationAndReactionPage',()=>{
  beforeEach(()=>setupMocks())
  it('renders the default cockpit, composition chart, and French LTR',async()=>{renderPage();expect(await screen.findByRole('heading',{level:1,name:'Et si un secteur s’arrêtait demain ?'})).toBeInTheDocument();expect(screen.getByTestId('simulation-year')).toHaveValue('2024');expect(screen.getByTestId('simulation-sector')).toHaveValue('extractive_activities');expect(screen.getByTestId('shock-slider')).toHaveValue('50');expect(screen.getByTestId('composition-chart')).toBeInTheDocument();expect(document.documentElement).toHaveAttribute('dir','ltr')})
  it('updates year, sector, slider preview, and sends the simulation request',async()=>{const user=userEvent.setup();renderPage();await screen.findByTestId('simulation-year');await user.selectOptions(screen.getByTestId('simulation-year'),'2023');await user.selectOptions(screen.getByTestId('simulation-sector'),'fishing');fireEvent.change(screen.getByTestId('shock-slider'),{target:{value:'75'}});expect(screen.getByTestId('shock-slider')).toHaveValue('75');await user.click(screen.getByRole('button',{name:'Simuler ce scénario'}));await waitFor(()=>expect(stress.simulateSingle).toHaveBeenCalledWith(2023,'fishing',75));expect(await screen.findByTestId('before-after-chart')).toBeInTheDocument()})
  it('supports quick percentages and chart sector selection',async()=>{const user=userEvent.setup();renderPage();await screen.findByTestId('simulation-year');await user.click(screen.getByRole('button',{name:'100%'}));expect(screen.getByTestId('shock-slider')).toHaveValue('100');await user.click(screen.getByTestId('composition-select-primary_sector'));expect(screen.getByTestId('simulation-sector')).toHaveValue('primary_sector')})
  it('shows the impact result and four-stage recommendation timeline',async()=>{const user=userEvent.setup();renderPage();await screen.findByTestId('simulation-year');await user.click(screen.getByRole('button',{name:'Simuler ce scénario'}));expect(await screen.findByText('Préserver les infrastructures')).toBeInTheDocument();expect(screen.getByTestId('recommendation-timeline')).toBeInTheDocument();expect(screen.getByText('0–3 mois')).toBeInTheDocument();expect(screen.getByText('Plus de 3 ans')).toBeInTheDocument();expect(screen.getByText('Pourquoi cette recommandation ?')).toBeInTheDocument()})
  it('runs demo mode with the real scenario inputs',async()=>{const user=userEvent.setup();renderPage();await screen.findByTestId('simulation-year');await user.click(screen.getByRole('button',{name:'Lancer la démonstration'}));await waitFor(()=>expect(stress.simulateSingle).toHaveBeenCalledWith(2024,'extractive_activities',100));expect(await screen.findByTestId('recommendation-timeline')).toBeInTheDocument()})
  it('supports Arabic RTL',async()=>{await i18n.changeLanguage('ar');renderPage();expect(await screen.findByRole('heading',{level:1,name:'ماذا لو توقف أحد القطاعات غداً؟'})).toBeInTheDocument();expect(document.documentElement).toHaveAttribute('dir','rtl')})
  it('uses a mobile-first stacked grid',async()=>{window.innerWidth=390;renderPage();await screen.findByTestId('cockpit-grid');expect(screen.getByTestId('cockpit-grid')).toHaveClass('grid');expect(screen.getByTestId('cockpit-grid').className).toContain('xl:grid-cols')})
  it('shows loading skeleton and backend-unavailable error',async()=>{let reject:(reason:Error)=>void=()=>{};vi.mocked(stress.loadSimulationPageData).mockReturnValue(new Promise((_,r)=>{reject=r}));renderPage();expect(screen.getByRole('status',{name:'Chargement'})).toBeInTheDocument();reject(new Error('network unavailable'));expect(await screen.findByText('Backend indisponible')).toBeInTheDocument();expect(screen.getByText('network unavailable')).toBeInTheDocument()})
})

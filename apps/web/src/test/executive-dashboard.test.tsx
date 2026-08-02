import {render,screen} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {MemoryRouter} from 'react-router-dom'
import {LanguageProvider} from '../contexts/LanguageContext'
import {EconomicIntelligenceDashboardPage} from '../pages/EconomicIntelligenceDashboardPage'
import * as dashboard from '../services/executiveDashboard'
vi.mock('../services/executiveDashboard',async()=>{const actual=await vi.importActual<typeof import('../services/executiveDashboard')>('../services/executiveDashboard');return {...actual,loadExecutiveDashboard:vi.fn()}})
const points=(a:number,b:number)=>[{year:2023,value:a},{year:2024,value:b}]
const series={gdp_activity_market_prices:points(900,1000),primary_sector:points(180,200),secondary_sector:points(270,300),tertiary_sector:points(450,500),agriculture_forestry:points(80,90),fishing:points(30,35),extractive_activities:points(100,120),manufacturing:points(70,80),construction_public_works:points(60,65),commerce:points(110,125),other_services:points(140,155),exports:points(200,220),imports:points(240,260)}
const data={overview:{latest_year:2024,latest_gdp_activity:1000,latest_gdp_expenditure:990,gdp_activity_growth_pct:11.11,largest_sector_code:'tertiary_sector',largest_sector_name_fr:'Tertiary',largest_sector_share_pct:50,fastest_growing_branch_name_fr:'Fishing',fastest_growing_branch_growth_pct:16.7,most_volatile_branch_name_fr:'Mining',most_volatile_branch_volatility:20,latest_trade_balance:-40,alert_count:0,completeness_score:100,unit:'Millions de MRU',price_type_note_fr:'Current prices',price_type_note_ar:'Current prices'},series}
const renderPage=()=>render(<LanguageProvider><MemoryRouter><EconomicIntelligenceDashboardPage/></MemoryRouter></LanguageProvider>)
describe('executive economic dashboard',()=>{beforeEach(()=>vi.mocked(dashboard.loadExecutiveDashboard).mockResolvedValue(data as never))
 it('loads latest KPIs and all decision charts',async()=>{renderPage();expect(await screen.findByText('PIB total')).toBeInTheDocument();expect(screen.getByTestId('gdp-structure-chart')).toBeInTheDocument();expect(screen.getByTestId('sector-evolution-chart')).toBeInTheDocument();expect(screen.getByTestId('gdp-without-mining-chart')).toBeInTheDocument();expect(screen.getByTestId('sector-share-donut')).toBeInTheDocument();expect(screen.getByTestId('sector-growth-heatmap')).toBeInTheDocument()})
 it('hides a sector line and links advanced workflows',async()=>{renderPage();const agriculture=await screen.findByRole('button',{name:/Agriculture/});await userEvent.click(agriculture);expect(agriculture).toHaveClass('text-slate-400');expect(document.querySelector('a[href="/explore?tab=compare"]')).toBeInTheDocument();expect(document.querySelector('a[href="/simulate"]')).toBeInTheDocument()})
})

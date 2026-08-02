import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Home } from './pages/Home'
import { NotFoundPage } from './pages/NotFoundPage'
import { ActivityPage, ComparePage, ExpenditurePage, MiningPage, OverviewPage, ReconciliationPage } from './pages/AnalyticalPages'
import { AlertsPage, CataloguePage, ForecastPage } from './pages/InteractivePages'
import { SimulationAndReactionPage } from './pages/SimulationAndReactionPage'
import { AssistantExperiencePage } from './pages/AssistantExperiencePage'
import { MultiComparePage } from './pages/MultiComparePage'
import { ReportsExperiencePage } from './pages/ReportsExperiencePage'
import { EconomicIntelligenceDashboardPage } from './pages/EconomicIntelligenceDashboardPage'

const pages = {overview:<OverviewPage/>,activity:<ActivityPage/>,mining:<MiningPage/>,expenditure:<ExpenditurePage/>,compare:<ComparePage/>,reconciliation:<ReconciliationPage/>,alerts:<AlertsPage/>,forecast:<ForecastPage/>,assistant:<AssistantExperiencePage/>,stress:<SimulationAndReactionPage/>,reports:<ReportsExperiencePage/>,catalogue:<CataloguePage/>}
const router = createBrowserRouter([{ path: '/', element: <Layout/>, errorElement: <NotFoundPage/>, children: [{ index: true, element: <Home/> }, ...Object.entries(pages).map(([path,element]) => ({ path, element })), {path:'simulate',element:<SimulationAndReactionPage/>},{path:'dashboard',element:<EconomicIntelligenceDashboardPage/>},{path:'explore',element:<MultiComparePage/>},{path:'assistant-reports',element:<ReportsExperiencePage/>}, { path: '*', element: <NotFoundPage/> }] }])
export function App() { return <RouterProvider router={router}/> }

import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Home } from './pages/Home'
import { NotFound } from './pages/NotFound'
import { ActivityPage, ComparePage, ExpenditurePage, MiningPage, OverviewPage, ReconciliationPage } from './pages/AnalyticalPages'
import { AlertsPage, AssistantPage, CataloguePage, ForecastPage, ReportsPage } from './pages/InteractivePages'
import { SimulationAndReactionPage } from './pages/SimulationAndReactionPage'

const pages = {overview:<OverviewPage/>,activity:<ActivityPage/>,mining:<MiningPage/>,expenditure:<ExpenditurePage/>,compare:<ComparePage/>,reconciliation:<ReconciliationPage/>,alerts:<AlertsPage/>,forecast:<ForecastPage/>,assistant:<AssistantPage/>,stress:<SimulationAndReactionPage/>,reports:<ReportsPage/>,catalogue:<CataloguePage/>}
const router = createBrowserRouter([{ path: '/', element: <Layout/>, errorElement: <NotFound/>, children: [{ index: true, element: <Home/> }, ...Object.entries(pages).map(([path,element]) => ({ path, element })), { path: '*', element: <NotFound/> }] }])
export function App() { return <RouterProvider router={router}/> }

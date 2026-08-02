import { lazy, Suspense, type ReactNode } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { Layout } from './components/Layout'
import { PageLoadingState } from './components/LoadingStates'

const Home = lazy(() => import('./pages/Home').then(module => ({ default: module.Home })))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage').then(module => ({ default: module.NotFoundPage })))
const OverviewPage = lazy(() => import('./pages/AnalyticalPages').then(module => ({ default: module.OverviewPage })))
const ActivityPage = lazy(() => import('./pages/AnalyticalPages').then(module => ({ default: module.ActivityPage })))
const MiningPage = lazy(() => import('./pages/AnalyticalPages').then(module => ({ default: module.MiningPage })))
const ExpenditurePage = lazy(() => import('./pages/AnalyticalPages').then(module => ({ default: module.ExpenditurePage })))
const ComparePage = lazy(() => import('./pages/AnalyticalPages').then(module => ({ default: module.ComparePage })))
const ReconciliationPage = lazy(() => import('./pages/AnalyticalPages').then(module => ({ default: module.ReconciliationPage })))
const AlertsPage = lazy(() => import('./pages/InteractivePages').then(module => ({ default: module.AlertsPage })))
const ForecastPage = lazy(() => import('./pages/InteractivePages').then(module => ({ default: module.ForecastPage })))
const CataloguePage = lazy(() => import('./pages/InteractivePages').then(module => ({ default: module.CataloguePage })))
const SimulationAndReactionPage = lazy(() => import('./pages/SimulationAndReactionPage').then(module => ({ default: module.SimulationAndReactionPage })))
const AssistantExperiencePage = lazy(() => import('./pages/AssistantExperiencePage').then(module => ({ default: module.AssistantExperiencePage })))
const MultiComparePage = lazy(() => import('./pages/MultiComparePage').then(module => ({ default: module.MultiComparePage })))
const ReportsExperiencePage = lazy(() => import('./pages/ReportsExperiencePage').then(module => ({ default: module.ReportsExperiencePage })))
const EconomicIntelligenceDashboardPage = lazy(() => import('./pages/EconomicIntelligenceDashboardPage').then(module => ({ default: module.EconomicIntelligenceDashboardPage })))

function load(component: ReactNode) { return <Suspense fallback={<PageLoadingState/>}>{component}</Suspense> }
const router = createBrowserRouter([{ path: '/', element: <Layout/>, errorElement: load(<NotFoundPage/>), children: [
  { index: true, element: load(<Home/>) },
  { path: 'overview', element: load(<OverviewPage/>) }, { path: 'activity', element: load(<ActivityPage/>) }, { path: 'mining', element: load(<MiningPage/>) }, { path: 'expenditure', element: load(<ExpenditurePage/>) }, { path: 'compare', element: load(<ComparePage/>) }, { path: 'reconciliation', element: load(<ReconciliationPage/>) },
  { path: 'alerts', element: load(<AlertsPage/> ) }, { path: 'forecast', element: load(<ForecastPage/> ) }, { path: 'catalogue', element: load(<CataloguePage/> ) },
  { path: 'assistant', element: load(<AssistantExperiencePage/>) }, { path: 'stress', element: load(<SimulationAndReactionPage/>) }, { path: 'reports', element: load(<ReportsExperiencePage/>) }, { path: 'simulate', element: load(<SimulationAndReactionPage/>) }, { path: 'dashboard', element: load(<EconomicIntelligenceDashboardPage/>) }, { path: 'explore', element: load(<MultiComparePage/>) }, { path: 'assistant-reports', element: load(<ReportsExperiencePage/>) }, { path: '*', element: load(<NotFoundPage/>) },
] }])

export function App() { return <RouterProvider router={router}/> }

import { Routes, Route } from 'react-router-dom'
import { PageLayout } from './components/layout/PageLayout'
import { HomePage } from './pages/HomePage'
import { RecentSpendingPage } from './pages/RecentSpendingPage'
import { DetailedSpendingPage } from './pages/DetailedSpendingPage'
import { RecordingExpensesPage } from './pages/RecordingExpensesPage'
import { LocationEditingPage } from './pages/LocationEditingPage'
import { HierarchyEditingPage } from './pages/HierarchyEditingPage'
import { IncomePage } from './pages/IncomePage'
import { DebugPage } from './pages/DebugPage'

function App() {
  return (
    <PageLayout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/recent-spending" element={<RecentSpendingPage />} />
        <Route path="/detailed-spending" element={<DetailedSpendingPage />} />
        <Route path="/recording-expenses" element={<RecordingExpensesPage />} />
        <Route path="/location-editing" element={<LocationEditingPage />} />
        <Route path="/hierarchy-editing" element={<HierarchyEditingPage />} />
        <Route path="/income" element={<IncomePage />} />
        <Route path="/debug" element={<DebugPage />} />
      </Routes>
    </PageLayout>
  )
}

export default App

import { Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from '../pages/Dashboard'
import IncidentAnalysis from '../pages/IncidentAnalysis'
import DemographyAnalysis from '../pages/DemographyAnalysis'
import InteractiveMap from '../pages/InteractiveMap'
import PredictionPage from '../pages/PredictionPage'
import Recommendations from '../pages/Recommendations'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/incidents" element={<IncidentAnalysis />} />
      <Route path="/demographics" element={<DemographyAnalysis />} />
      <Route path="/map" element={<InteractiveMap />} />
      <Route path="/predictions" element={<PredictionPage />} />
      <Route path="/recommendations" element={<Recommendations />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default AppRoutes

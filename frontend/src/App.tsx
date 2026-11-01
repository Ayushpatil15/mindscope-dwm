import React, { useState } from 'react';
import { AppShell } from './components/AppShell';
import { DashboardScreen } from './screens/Dashboard';
import { DataExplorationScreen } from './screens/DataExploration';
import { OLAPStudioScreen } from './screens/OLAPStudio';
import { MarketBasketScreen } from './screens/MarketBasket';
import { SegmentationScreen } from './screens/Segmentation';
import { PredictionScreen } from './screens/Prediction';
import { InsightsScreen } from './screens/Insights';
import { LabPageScreen } from './screens/LabPage';

export const App: React.FC = () => {
  const [activeScreen, setActiveScreen] = useState<string>('dashboard');

  const renderScreen = () => {
    switch (activeScreen) {
      case 'dashboard':
        return <DashboardScreen />;
      case 'exploration':
        return <DataExplorationScreen />;
      case 'sales':
        return <OLAPStudioScreen />;
      case 'market-basket':
        return <MarketBasketScreen />;
      case 'segmentation':
        return <SegmentationScreen />;
      case 'predict':
        return <PredictionScreen />;
      case 'insights':
        return <InsightsScreen />;
      default:
        if (activeScreen.startsWith('lab-')) {
          const num = parseInt(activeScreen.replace('lab-', ''), 10) || 1;
          return <LabPageScreen labNumber={num} />;
        }
        return <DashboardScreen />;
    }
  };

  return (
    <AppShell activeScreen={activeScreen} onNavigate={setActiveScreen}>
      {renderScreen()}
    </AppShell>
  );
};

export default App;

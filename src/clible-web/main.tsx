import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { AuthProvider } from './AuthContext.tsx';
import { SettingsProvider } from './user/SettingsContext.tsx';
import { ReadingPlanProvider } from './user/ReadingPlanContext.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <SettingsProvider>
        <ReadingPlanProvider>
          <App />
        </ReadingPlanProvider>
      </SettingsProvider>
    </AuthProvider>
  </StrictMode>,
);

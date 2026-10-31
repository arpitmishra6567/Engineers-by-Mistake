import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppLayout } from './components/layout/AppLayout';
import { OverviewPage } from './pages/OverviewPage';
import { NewRepairPage } from './pages/NewRepairPage';
import { LiveExecutionPage } from './pages/LiveExecutionPage';
import { PatchReviewPage } from './pages/PatchReviewPage';
import { VerificationPage } from './pages/VerificationPage';
import { EvaluationsPage } from './pages/EvaluationsPage';
import { ModelsSkillsPage } from './pages/ModelsSkillsPage';
import { RepositoriesPage } from './pages/RepositoriesPage';
import { SettingsPage } from './pages/SettingsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 3000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<OverviewPage />} />
            <Route path="new" element={<NewRepairPage />} />
            <Route path="execution" element={<LiveExecutionPage />} />
            <Route path="patch-review" element={<PatchReviewPage />} />
            <Route path="verification" element={<VerificationPage />} />
            <Route path="evaluations" element={<EvaluationsPage />} />
            <Route path="models-skills" element={<ModelsSkillsPage />} />
            <Route path="repositories" element={<RepositoriesPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};


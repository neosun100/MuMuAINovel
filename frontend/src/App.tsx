import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import ProjectList from './pages/ProjectList';
import ProjectWizardNew from './pages/ProjectWizardNew';
import Inspiration from './pages/Inspiration';
import ProjectDetail from './pages/ProjectDetail';
import WorldSetting from './pages/WorldSetting';
import Outline from './pages/Outline';
import Characters from './pages/Characters';
import Careers from './pages/Careers';
import Relationships from './pages/Relationships';
import Organizations from './pages/Organizations';
import Chapters from './pages/Chapters';
import ChapterReader from './pages/ChapterReader';
import ChapterAnalysis from './pages/ChapterAnalysis';
import WritingStyles from './pages/WritingStyles';
import RefinementReview from './pages/RefinementReview';
import Settings from './pages/Settings';
import MCPPlugins from './pages/MCPPlugins';
import UserManagement from './pages/UserManagement';
import PromptTemplates from './pages/PromptTemplates';
import Sponsor from './pages/Sponsor';
// import Polish from './pages/Polish';
import Login from './pages/Login';
import AuthCallback from './pages/AuthCallback';
import ProtectedRoute from './components/ProtectedRoute';
import AppFooter from './components/AppFooter';
import './App.css';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <Routes>
          <Route path="/login" element={<><Login /><AppFooter /></>} />
          <Route path="/auth/callback" element={<AuthCallback />} />

          <Route path="/" element={<ProtectedRoute><><ProjectList /><AppFooter /></></ProtectedRoute>} />
          <Route path="/projects" element={<ProtectedRoute><><ProjectList /><AppFooter /></></ProtectedRoute>} />
          <Route path="/wizard" element={<ProtectedRoute><ProjectWizardNew /></ProtectedRoute>} />
          <Route path="/inspiration" element={<ProtectedRoute><Inspiration /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          <Route path="/prompt-templates" element={<ProtectedRoute><><PromptTemplates /><AppFooter /></></ProtectedRoute>} />
          <Route path="/mcp-plugins" element={<ProtectedRoute><MCPPlugins /></ProtectedRoute>} />
          <Route path="/user-management" element={<ProtectedRoute><UserManagement /></ProtectedRoute>} />
          <Route path="/chapters/:chapterId/reader" element={<ProtectedRoute><ChapterReader /></ProtectedRoute>} />
          <Route path="/project/:projectId" element={<ProtectedRoute><ProjectDetail /></ProtectedRoute>}>
            <Route index element={<Navigate to="sponsor" replace />} />
            <Route path="world-setting" element={<WorldSetting />} />
            <Route path="careers" element={<Careers />} />
            <Route path="outline" element={<Outline />} />
            <Route path="characters" element={<Characters />} />
            <Route path="relationships" element={<Relationships />} />
            <Route path="organizations" element={<Organizations />} />
            <Route path="chapters" element={<Chapters />} />
            <Route path="chapter-analysis" element={<ChapterAnalysis />} />
            <Route path="writing-styles" element={<WritingStyles />} />
            <Route path="refinement-review" element={<RefinementReview />} />
            <Route path="sponsor" element={<Sponsor />} />
            {/* <Route path="polish" element={<Polish />} /> */}
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;

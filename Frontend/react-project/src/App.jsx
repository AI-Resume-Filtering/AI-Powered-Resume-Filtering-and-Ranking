import { BrowserRouter, Routes, Route } from "react-router-dom";

import Index from "./pages/Index";
import AboutProject from "./pages/AboutProject";
import CompanyLogin from "./pages/CompanyLogin";
import CompanyRegister from "./pages/CompanyRegister";
import CompanyDashboard from "./pages/dashboard/CompanyDashboard";
import JobList from "./pages/JobList";
import ApplyJob from "./pages/ApplyJob";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import { BackgroundTasksProvider } from "./context/BackgroundTasksContext";
import BackgroundTaskTray from "./components/BackgroundTaskTray";

function App() {
  return (
    <BrowserRouter>
      <BackgroundTasksProvider>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/about-project" element={<AboutProject />} />
          <Route path="/company-login" element={<CompanyLogin />} />
          <Route path="/company-register" element={<CompanyRegister />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />

          <Route
            path="/company-dashboard"
            element={<CompanyDashboard />}
          />

          <Route path="/jobs" element={<JobList />} />
          <Route path="/apply-job" element={<ApplyJob />} />
        </Routes>
        <BackgroundTaskTray />
      </BackgroundTasksProvider>
    </BrowserRouter>
  );
}

export default App;
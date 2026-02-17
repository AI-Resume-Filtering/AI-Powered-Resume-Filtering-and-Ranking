import { BrowserRouter, Routes, Route } from "react-router-dom";

import Index from "./pages/Index";
import CompanyLogin from "./pages/CompanyLogin";
import CompanyRegister from "./pages/CompanyRegister";
import CompanyDashboard from "./pages/dashboard/CompanyDashboard";
import JobList from "./pages/JobList";
import ApplyJob from "./pages/ApplyJob";
import ForgotPassword from "./pages/ForgotPassword";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Index />} />
        <Route path="/company-login" element={<CompanyLogin />} />
        <Route path="/company-register" element={<CompanyRegister />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        <Route
          path="/company-dashboard"
          element={<CompanyDashboard />}
        />

        <Route path="/jobs" element={<JobList />} />
        <Route path="/apply-job" element={<ApplyJob />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
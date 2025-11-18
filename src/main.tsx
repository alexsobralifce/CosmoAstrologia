import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from "react-router-dom";
import App from "./App.tsx";
import { AuthCallback } from "./pages/AuthCallback.tsx";
import { useEffect } from "react";
import "./index.css";

// Component to handle OAuth callback and route handling
function AppRouter() {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Handle OAuth callback
    if (location.pathname === '/auth/callback') {
      return; // AuthCallback component will handle it
    }

    // Check for pending onboarding after auth
    const token = localStorage.getItem('auth_token');
    const pendingOnboarding = localStorage.getItem('pending_onboarding');
    
    if (token && pendingOnboarding && location.pathname === '/') {
      // User just authenticated, redirect to onboarding completion
      const data = JSON.parse(pendingOnboarding);
      navigate('/dashboard', { 
        state: { 
          onboardingData: {
            name: data.name,
            birthDate: new Date(data.birthDate),
            birthTime: data.birthTime,
            birthPlace: data.birthPlace
          }
        } 
      });
      localStorage.removeItem('pending_onboarding');
    }
  }, [location, navigate]);

  return (
    <Routes>
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route path="/*" element={<App />} />
    </Routes>
  );
}

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <AppRouter />
  </BrowserRouter>
);
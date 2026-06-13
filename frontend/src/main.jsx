import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Banknote, Boxes, CalendarCheck, Factory, LayoutDashboard, LogOut, PackagePlus, ReceiptText, ShieldCheck, Users, Warehouse } from "lucide-react";

import "./styles.css";
import { api, setAuthToken } from "./api/client";
import { AuthContext } from "./auth/context";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ProductsPage } from "./pages/ProductsPage";
import { InventoryPage } from "./pages/InventoryPage";
import { EmployeesPage } from "./pages/EmployeesPage";
import { AttendancePage } from "./pages/AttendancePage";
import { SalesPage } from "./pages/SalesPage";
import { PayrollPage } from "./pages/PayrollPage";
import { FinancePage } from "./pages/FinancePage";
import { ProductionPage } from "./pages/ProductionPage";

function Shell({ children }) {
  const { user, logout } = React.useContext(AuthContext);
  return (
    <div className="appShell">
      <aside className="sidebar">
        <div className="brand">
          <ShieldCheck size={26} />
          <div>
            <strong>Smart CRM</strong>
            <span>Small business OS</span>
          </div>
        </div>
        <nav>
          <a href="/"><LayoutDashboard size={18} /> Dashboard</a>
          <a href="/products"><PackagePlus size={18} /> Products</a>
          <a href="/inventory"><Warehouse size={18} /> Inventory</a>
          <a href="/sales"><ReceiptText size={18} /> Sales</a>
          <a href="/employees"><Users size={18} /> Employees</a>
          <a href="/attendance"><CalendarCheck size={18} /> Attendance</a>
          <a href="/payroll"><Banknote size={18} /> Payroll</a>
          <a href="/finance"><Banknote size={18} /> Profit/Loss</a>
          <a href="/production"><Factory size={18} /> Production</a>
        </nav>
        <div className="account">
          <div>
            <strong>{user?.full_name}</strong>
            <span>{user?.role}</span>
          </div>
          <button className="iconButton" title="Sign out" onClick={logout}><LogOut size={18} /></button>
        </div>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    setAuthToken(token);
  }, [token]);

  const auth = useMemo(() => ({
    token,
    user,
    login: (payload) => {
      localStorage.setItem("token", payload.access_token);
      localStorage.setItem("user", JSON.stringify(payload.user));
      setToken(payload.access_token);
      setUser(payload.user);
    },
    logout: () => {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setToken(null);
      setUser(null);
    },
  }), [token, user]);

  return (
    <AuthContext.Provider value={auth}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={token ? <Navigate to="/" /> : <LoginPage />} />
          <Route path="/" element={<ProtectedRoute><Shell><DashboardPage /></Shell></ProtectedRoute>} />
          <Route path="/products" element={<ProtectedRoute><Shell><ProductsPage /></Shell></ProtectedRoute>} />
          <Route path="/inventory" element={<ProtectedRoute><Shell><InventoryPage /></Shell></ProtectedRoute>} />
          <Route path="/sales" element={<ProtectedRoute><Shell><SalesPage /></Shell></ProtectedRoute>} />
          <Route path="/employees" element={<ProtectedRoute><Shell><EmployeesPage /></Shell></ProtectedRoute>} />
          <Route path="/attendance" element={<ProtectedRoute><Shell><AttendancePage /></Shell></ProtectedRoute>} />
          <Route path="/payroll" element={<ProtectedRoute><Shell><PayrollPage /></Shell></ProtectedRoute>} />
          <Route path="/finance" element={<ProtectedRoute><Shell><FinancePage /></Shell></ProtectedRoute>} />
          <Route path="/production" element={<ProtectedRoute><Shell><ProductionPage /></Shell></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthContext.Provider>
  );
}

createRoot(document.getElementById("root")).render(<App />);

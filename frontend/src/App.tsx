import { NavLink, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Alerts from './pages/Alerts';
import Dashboard from './pages/Dashboard';
import Journal from './pages/Journal';
import Portfolio from './pages/Portfolio';

const navItems = [
  { to: '/', label: 'Portfolios', end: true },
  { to: '/alerts', label: 'Alerts', end: false },
  { to: '/journal', label: 'Journal', end: false },
];

export default function App() {
  return (
    <Router>
      <div className="relative min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/portfolio/:id" element={<Portfolio />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/journal" element={<Journal />} />
        </Routes>

        {/* Bottom navigation */}
        <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex justify-around py-2 z-20">
          {navItems.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex flex-col items-center text-xs py-1 px-4 rounded-lg font-medium transition-colors ${
                  isActive ? 'text-blue-600' : 'text-gray-500'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </Router>
  );
}

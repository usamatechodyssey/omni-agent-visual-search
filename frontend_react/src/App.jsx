import { BrowserRouter, Routes, Route, Link, NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import ProtectedRoute from './components/ProtectedRoute'
import { getAccessToken, clearTokens } from './services/api'
import { ToastProvider } from './components/ui/Toast' // 🔥 Import add kiya

function AppContent() {
  const location = useLocation()
  const navigate = useNavigate()
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  // Route change hone par check hota hai ke user logged in hai ya nahi
  useEffect(() => {
    setIsLoggedIn(!!getAccessToken())
  }, [location])

  const handleLogout = () => {
    clearTokens()
    setIsLoggedIn(false)
    navigate('/')
  }

  return (
    <ToastProvider> {/* 🔥 ToastProvider wrap kiya */}
      <div className="min-h-screen flex flex-col bg-dark-900 text-slate-200 font-sans">
        {/* Navbar */}
        <nav className="bg-dark-800 border-b border-gray-700 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center gap-8">
                <Link to="/" className="text-2xl font-bold gradient-text">
                  OmniAgent
                </Link>
                <div className="hidden md:flex gap-6">
                  <NavLink to="/" className={({ isActive }) => isActive ? 'text-cyan-400 font-medium' : 'text-slate-300 hover:text-white'}>Home</NavLink>
                  <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'text-cyan-400 font-medium' : 'text-slate-300 hover:text-white'}>Dashboard</NavLink>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                {isLoggedIn ? (
                  <button 
                    onClick={handleLogout}
                    className="text-sm font-medium text-slate-300 hover:text-red-400"
                  >
                    Logout
                  </button>
                ) : (
                  <>
                    <Link to="/login" className="text-sm font-medium text-slate-300 hover:text-white">Login</Link>
                    <Link to="/register" className="btn-primary text-white px-4 py-2 rounded-md text-sm font-medium">Get Started</Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-grow">
          <Routes>
            {/* 🔥 Yahan isLoggedIn prop pass ho raha hai */}
            <Route path="/" element={<Home isLoggedIn={isLoggedIn} />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-dark-800 border-t border-gray-700 py-6">
          <div className="max-w-7xl mx-auto px-4 text-center text-sm text-slate-400">
            © 2026 OmniAgent Core. All rights reserved.
          </div>
        </footer>
      </div>
    </ToastProvider>
  )
}

// Main App - Router ko wrap karta hai
function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  )
}

export default App
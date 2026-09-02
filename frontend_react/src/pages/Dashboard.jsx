// import { useState, useEffect } from 'react'
// import { useNavigate } from 'react-router-dom'
// import { SettingsAPI, VisualAPI, clearTokens } from '../services/api'
// import Button from '../components/ui/Button'
// import { useToast } from '../components/ui/Toast'
// import OnboardingGuide from '../components/onboarding/OnboardingGuide'
// import IntegrationsHub from '../components/dashboard/IntegrationsHub'
// import ApiKeyDisplay from '../components/onboarding/ApiKeyDisplay'
// import JobsHistory from '../components/dashboard/JobsHistory' // 🔥 JobsHistory Import
// import VisualSearchTester from '../components/dashboard/VisualSearchTester' // 🔥 VisualSearchTester Import

// export default function Dashboard() {
//   const [integrations, setIntegrations] = useState([])
//   const [userEmail, setUserEmail] = useState('')
//   const [apiKey, setApiKey] = useState('')
  
//   const [activeTab, setActiveTab] = useState('overview')
//   const [showGuide, setShowGuide] = useState(false)

//   const [loading, setLoading] = useState(true)
//   const [error, setError] = useState('')

//   const [syncJobId, setSyncJobId] = useState(null)
//   const [syncStatus, setSyncStatus] = useState('')
//   const [syncLoading, setSyncLoading] = useState(false)
//   const [statusLoading, setStatusLoading] = useState(false)
  
//   const navigate = useNavigate()
//   const { addToast } = useToast()

//   const handleLogout = () => {
//     clearTokens()
//     navigate('/login')
//   }

//   // 🔥 Fetch Integrations Function (Isko onIntegrationsChange mein pass karenge)
//   const fetchIntegrations = async () => {
//     setLoading(true)
//     setError('')
//     try {
//       const data = await SettingsAPI.getIntegrations()
//       setIntegrations(data.connected_services || [])
//       setUserEmail(data.user_email || '')
//       setApiKey(data.api_key || '')
//     } catch (err) {
//       if (err.message.includes('Session expired')) {
//         handleLogout()
//       } else {
//         setError(err.message || 'Failed to load integrations')
//       }
//     } finally {
//       setLoading(false)
//     }
//   }

//   useEffect(() => {
//     fetchIntegrations()
//   }, [])

//   const hasVectorDB = integrations.some(svc => svc.provider === 'qdrant' || svc.provider === 'mongodb' || svc.provider === 'pinecone')
//   const hasDataSource = integrations.some(svc => svc.provider === 'shopify' || svc.provider === 'woocommerce' || svc.provider === 'mongodb_store' || svc.provider === 'sanity')
//   const canSync = hasVectorDB && hasDataSource

//   const handleSync = async () => {
//     setSyncLoading(true)
//     setSyncStatus('')
//     setSyncJobId(null)
//     try {
//       const data = await VisualAPI.triggerSync()
//       setSyncJobId(data.job_id)
//       setSyncStatus('Processing...')
//       addToast('Visual Sync started successfully!', 'success')
//     } catch (err) {
//       setSyncStatus(`Error: ${err.message}`)
//       addToast(`Error: ${err.message}`, 'error')
//     } finally {
//       setSyncLoading(false)
//     }
//   }

//   const handleCheckStatus = async (jobId) => {
//     setStatusLoading(true)
//     try {
//       const data = await VisualAPI.getJobStatus(jobId)
//       setSyncStatus(data.status)
//       if (data.error_message) {
//         setSyncStatus(`Failed: ${data.error_message}`)
//         addToast(`Sync failed: ${data.error_message}`, 'error')
//       } else if (data.status === 'completed') {
//         addToast('Sync completed successfully!', 'success')
//       }
//     } catch (err) {
//       setSyncStatus(`Error checking status: ${err.message}`)
//     } finally {
//       setStatusLoading(false)
//     }
//   }

//   if (loading) {
//     return <div className="p-8 text-center text-slate-400 bg-dark-900 min-h-screen">Loading Dashboard...</div>
//   }

//   return (
//     <div className="flex flex-1 overflow-hidden bg-dark-900">
//       {/* Sidebar */}
//       <aside className="w-64 bg-dark-800 border-r border-gray-700 hidden md:flex flex-col">
//         <div className="p-6">
//           <h2 className="text-xl font-bold text-white">OmniAgent</h2>
//           <ul className="mt-6 space-y-4">
//             <li onClick={() => setActiveTab('overview')} className={`cursor-pointer ${activeTab === 'overview' ? 'text-cyan-400 font-medium' : 'text-slate-300 hover:text-white'}`}>Dashboard</li>
//             <li onClick={() => setActiveTab('integrations')} className={`cursor-pointer ${activeTab === 'integrations' ? 'text-cyan-400 font-medium' : 'text-slate-300 hover:text-white'}`}>Integrations</li>
//             <li onClick={() => setActiveTab('billing')} className={`cursor-pointer ${activeTab === 'billing' ? 'text-cyan-400 font-medium' : 'text-slate-300 hover:text-white'}`}>Billing</li>
//           </ul>
//           <Button variant="danger" className="mt-10 w-full" onClick={handleLogout}>Logout</Button>
//         </div>
//       </aside>

//       {/* Main Content (Scrollable) */}
//       <main className="flex-1 overflow-y-auto p-8">
//         <div className="flex justify-between items-center mb-6">
//           <h1 className="text-2xl font-bold text-white">
//             {activeTab === 'overview' ? 'Dashboard Overview' : activeTab === 'integrations' ? 'Integrations Hub' : 'Billing & Subscription'}
//           </h1>
//           <button onClick={() => setShowGuide(true)} className="text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-2">
//             ❓ How it works?
//           </button>
//         </div>
        
//         {error && (
//           <div className="mb-4 rounded-md bg-red-500/10 p-4 text-sm text-red-400">
//             {error}
//           </div>
//         )}

//         {activeTab === 'integrations' && (
//           <IntegrationsHub 
//             apiKey={apiKey} 
//             integrations={integrations} // 🔥 Pass kiya
//             onIntegrationsChange={fetchIntegrations} // 🔥 Pass kiya
//             onBack={() => setActiveTab('overview')} 
//           />
//         )}

//         {activeTab === 'billing' && (
//           <div className="glass p-6 rounded-lg shadow">
//             <h3 className="text-lg font-medium text-white mb-4">Billing & Subscription</h3>
//             <p className="text-slate-400">Payment adapter (EasyPaisa/JazzCash/Stripe) yahan jald hi add hoga.</p>
//           </div>
//         )}

//         {activeTab === 'overview' && (
//           <>
//             <div className="glass p-6 rounded-lg shadow mb-6">
//               <p className="text-sm text-slate-400">Logged in as:</p>
//               <p className="text-lg font-semibold text-white">{userEmail}</p>
//             </div>

//             {apiKey && (
//               <div className="mb-6">
//                 <ApiKeyDisplay apiKey={apiKey} />
//               </div>
//             )}

//             <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
//               <div className="glass p-6 rounded-lg shadow">
//                 <h3 className="text-lg font-medium text-white mb-2">Vector DB</h3>
//                 <p className="text-sm text-slate-400">Status: {hasVectorDB ? 'Connected' : 'Not Connected'}</p>
//               </div>
//               <div className="glass p-6 rounded-lg shadow">
//                 <h3 className="text-lg font-medium text-white mb-2">Data Source</h3>
//                 <p className="text-sm text-slate-400">Status: {hasDataSource ? 'Connected' : 'Not Connected'}</p>
//               </div>
//             </div>

//             <div className="glass p-6 rounded-lg shadow">
//               <h3 className="text-lg font-medium text-white mb-4">Visual Sync</h3>
              
//               {!canSync && (
//                 <p className="text-sm text-amber-500 mb-4">
//                   ⚠️ Please connect your Vector DB and Data Source first to enable Sync.
//                 </p>
//               )}

//               <Button onClick={handleSync} disabled={!canSync || syncLoading} variant="primary">
//                 {syncLoading ? 'Starting...' : 'Start Visual Sync'}
//               </Button>
              
//               {syncStatus && (
//                 <div className="mt-4 p-4 bg-dark-800 rounded-md">
//                   <p className="text-sm text-slate-300">Status: <span className="font-medium text-cyan-400">{syncStatus}</span></p>
//                   {syncJobId && (
//                     <Button onClick={() => handleCheckStatus(syncJobId)} variant="ghost" size="sm" className="mt-2">
//                       {statusLoading ? 'Checking...' : 'Refresh Status'}
//                     </Button>
//                   )}
//                 </div>
//               )}
//             </div>

//             {/* 🔥 JobsHistory & VisualSearchTester Yahan Add Kiye */}
//             <div className="mt-6">
//               <JobsHistory />
//             </div>

//             <div className="mt-6">
//               <VisualSearchTester apiKey={apiKey} />
//             </div>
//           </>
//         )}
//       </main>

//       <OnboardingGuide isOpen={showGuide} onClose={() => setShowGuide(false)} />
//     </div>
//   )
// }
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { SettingsAPI, VisualAPI, clearTokens } from '../services/api'
import Button from '../components/ui/Button'
import { useToast } from '../components/ui/Toast'
import OnboardingGuide from '../components/onboarding/OnboardingGuide'
import IntegrationsHub from '../components/dashboard/IntegrationsHub'
import ApiKeyDisplay from '../components/onboarding/ApiKeyDisplay'
import JobsHistory from '../components/dashboard/JobsHistory'
import VisualSearchTester from '../components/dashboard/VisualSearchTester'
import IntegrateTab from '../components/integrate/IntegrateTab'

export default function Dashboard() {
  const [integrations, setIntegrations] = useState([])
  const [userEmail, setUserEmail] = useState('')
  const [apiKey, setApiKey] = useState('')
  
  const [activeTab, setActiveTab] = useState('overview')
  const [showGuide, setShowGuide] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [syncJobId, setSyncJobId] = useState(null)
  const [syncStatus, setSyncStatus] = useState('')
  const [syncLoading, setSyncLoading] = useState(false)
  const [statusLoading, setStatusLoading] = useState(false)
  
  const navigate = useNavigate()
  const { addToast } = useToast()

  const handleLogout = () => {
    clearTokens()
    navigate('/login')
  }

  const fetchIntegrations = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await SettingsAPI.getIntegrations()
      setIntegrations(data.connected_services || [])
      setUserEmail(data.user_email || '')
      setApiKey(data.api_key || '')
    } catch (err) {
      if (err.message.includes('Session expired')) {
        handleLogout()
      } else {
        setError(err.message || 'Failed to load integrations')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchIntegrations()
  }, [])

  const hasVectorDB = integrations.some(svc => svc.provider === 'qdrant' || svc.provider === 'mongodb' || svc.provider === 'pinecone')
  const hasDataSource = integrations.some(svc => svc.provider === 'shopify' || svc.provider === 'woocommerce' || svc.provider === 'mongodb_store' || svc.provider === 'sanity')
  const canSync = hasVectorDB && hasDataSource

  const handleSync = async () => {
    setSyncLoading(true)
    setSyncStatus('')
    setSyncJobId(null)
    try {
      const data = await VisualAPI.triggerSync()
      setSyncJobId(data.job_id)
      setSyncStatus('Processing...')
      addToast('Visual Sync started successfully!', 'success')
    } catch (err) {
      setSyncStatus(`Error: ${err.message}`)
      addToast(`Error: ${err.message}`, 'error')
    } finally {
      setSyncLoading(false)
    }
  }

  const handleCheckStatus = async (jobId) => {
    setStatusLoading(true)
    try {
      const data = await VisualAPI.getJobStatus(jobId)
      setSyncStatus(data.status)
      if (data.error_message) {
        setSyncStatus(`Failed: ${data.error_message}`)
        addToast(`Sync failed: ${data.error_message}`, 'error')
      } else if (data.status === 'completed') {
        addToast('Sync completed successfully!', 'success')
      }
    } catch (err) {
      setSyncStatus(`Error checking status: ${err.message}`)
    } finally {
      setStatusLoading(false)
    }
  }

  if (loading) {
    return <div className="p-8 text-center text-slate-400 bg-dark-900 min-h-screen">Loading Dashboard...</div>
  }

  const handleTabClick = (tab) => {
    setActiveTab(tab)
    setIsSidebarOpen(false)
  }

  return (
    <div className="flex flex-1 overflow-hidden bg-dark-900">
      
      {/* 🔥 Mobile Backdrop - Solid Black Opaque (Content piche dikhna band) */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 z-[65] bg-black/90 md:hidden" 
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* 🔥 Sidebar - Solid Dark Background & High Z-Index */}
      <aside className={`fixed inset-y-0 left-0 z-[70] w-64 bg-dark-800 border-r border-gray-700 transform transition-transform duration-300 md:relative md:translate-x-0 md:flex ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="p-6">
          <h2 className="text-xl font-bold text-white">OmniAgent</h2>
          <ul className="mt-6 space-y-4">
            <li onClick={() => handleTabClick('overview')} className={`cursor-pointer ${activeTab === 'overview' ? 'text-cyan-400 font-medium' : 'text-slate-300 hover:text-white'}`}>Dashboard</li>
            <li onClick={() => handleTabClick('integrations')} className={`cursor-pointer ${activeTab === 'integrations' ? 'text-cyan-400 font-medium' : 'text-slate-300 hover:text-white'}`}>Integrations</li>
            <li onClick={() => handleTabClick('integrate')} className={`cursor-pointer ${activeTab === 'integrate' ? 'text-cyan-400 font-medium' : 'text-slate-300 hover:text-white'}`}>Integrate</li>
            <li onClick={() => handleTabClick('billing')} className={`cursor-pointer ${activeTab === 'billing' ? 'text-cyan-400 font-medium' : 'text-slate-300 hover:text-white'}`}>Billing</li>
          </ul>
          <Button variant="danger" className="mt-10 w-full" onClick={handleLogout}>Logout</Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative">
        
        {/* 🔥 Mobile Header - Solid Opaque Background + Sticky */}
        <div className="sticky top-0 z-[30] flex items-center justify-between p-4 bg-dark-900 border-b border-gray-700 md:hidden">
          <button onClick={() => setIsSidebarOpen(true)} className="text-cyan-400 text-2xl">
            ☰
          </button>
          <h2 className="text-xl font-bold text-white">OmniAgent</h2>
        </div>

        <div className="p-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-white">
              {activeTab === 'overview' ? 'Dashboard Overview' : activeTab === 'integrations' ? 'Integrations Hub' : activeTab === 'integrate' ? 'Integrate Visual Search' : 'Billing & Subscription'}
            </h1>
            <button onClick={() => setShowGuide(true)} className="text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-2 hidden md:flex">
              ❓ How it works?
            </button>
          </div>
          
          {error && (
            <div className="mb-4 rounded-md bg-red-500/10 p-4 text-sm text-red-400">
              {error}
            </div>
          )}

          {activeTab === 'integrations' && (
            <IntegrationsHub 
              apiKey={apiKey} 
              integrations={integrations}
              onIntegrationsChange={fetchIntegrations}
              onBack={() => handleTabClick('overview')} 
            />
          )}

          {activeTab === 'integrate' && (
            <IntegrateTab apiKey={apiKey} />
          )}

          {activeTab === 'billing' && (
            <div className="glass p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-white mb-4">Billing & Subscription</h3>
              <p className="text-slate-400">Payment adapter (EasyPaisa/JazzCash/Stripe) yahan jald hi add hoga.</p>
            </div>
          )}

          {activeTab === 'overview' && (
            <>
              <div className="glass p-6 rounded-lg shadow mb-6">
                <p className="text-sm text-slate-400">Logged in as:</p>
                <p className="text-lg font-semibold text-white">{userEmail}</p>
              </div>

              {apiKey && (
                <div className="mb-6">
                  <ApiKeyDisplay apiKey={apiKey} />
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="glass p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-white mb-2">Vector DB</h3>
                  <p className="text-sm text-slate-400">Status: {hasVectorDB ? 'Connected' : 'Not Connected'}</p>
                </div>
                <div className="glass p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-white mb-2">Data Source</h3>
                  <p className="text-sm text-slate-400">Status: {hasDataSource ? 'Connected' : 'Not Connected'}</p>
                </div>
              </div>

              <div className="glass p-6 rounded-lg shadow">
                <h3 className="text-lg font-medium text-white mb-4">Visual Sync</h3>
                
                {!canSync && (
                  <p className="text-sm text-amber-500 mb-4">
                    ⚠️ Please connect your Vector DB and Data Source first to enable Sync.
                  </p>
                )}

                <Button onClick={handleSync} disabled={!canSync || syncLoading} variant="primary">
                  {syncLoading ? 'Starting...' : 'Start Visual Sync'}
                </Button>
                
                {syncStatus && (
                  <div className="mt-4 p-4 bg-dark-800 rounded-md">
                    <p className="text-sm text-slate-300">Status: <span className="font-medium text-cyan-400">{syncStatus}</span></p>
                    {syncJobId && (
                      <Button onClick={() => handleCheckStatus(syncJobId)} variant="ghost" size="sm" className="mt-2">
                        {statusLoading ? 'Checking...' : 'Refresh Status'}
                      </Button>
                    )}
                  </div>
                )}
              </div>

              <div className="mt-6">
                <JobsHistory />
              </div>

              <div className="mt-6">
                <VisualSearchTester apiKey={apiKey} />
              </div>
            </>
          )}
        </div>
      </main>

      <OnboardingGuide isOpen={showGuide} onClose={() => setShowGuide(false)} />
    </div>
  )
}
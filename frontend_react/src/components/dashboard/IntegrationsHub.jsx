import { useState } from 'react'
import SetupWizard from '../onboarding/SetupWizard'
import ApiKeyDisplay from '../onboarding/ApiKeyDisplay'
import Button from '../ui/Button'
import { useToast } from '../ui/Toast'
import { SettingsAPI } from '../../services/api'
import FileUpload from './FileUpload' // 🔥 Import add kiya

export default function IntegrationsHub({ apiKey, integrations, onIntegrationsChange, onBack }) {
  const [wizardType, setWizardType] = useState(null) // 'vector' | 'store' | null
  
  // 🔥 State Added
  const [selectedProvider, setSelectedProvider] = useState('')
  const [selectedCollection, setSelectedCollection] = useState('')
  
  const { addToast } = useToast()

  // 🔥 Handler Added
  const handleSelectVectorDB = async () => {
    if (!selectedProvider || !selectedCollection) {
      addToast('Please select both a Vector DB provider and collection name.', 'error')
      return
    }
    try {
      await SettingsAPI.selectVectorDB(selectedProvider, selectedCollection)
      addToast('Vector DB selected successfully!', 'success')
      onIntegrationsChange() // Refresh parent
    } catch (err) {
      addToast(`Error: ${err.message}`, 'error')
    }
  }

  // Delete Integration Function
  const handleDelete = async (provider) => {
    if (!window.confirm(`Are you sure you want to delete ${provider}?`)) return

    try {
      await SettingsAPI.deleteIntegration(provider)
      addToast(`${provider} deleted successfully!`, 'success')
      onIntegrationsChange()
    } catch (err) {
      addToast(`Error: ${err.message}`, 'error')
    }
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <div className="flex justify-end items-center mb-4">
        <button onClick={onBack} className="text-slate-400 hover:text-white text-sm">← Back to Dashboard</button>
      </div>

      {/* CONNECTED SERVICES LIST (Delete Section) */}
      {integrations.length > 0 && (
        <div className="glass p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-white mb-4">Connected Services</h3>
          <ul className="space-y-3">
            {integrations.map((svc) => (
              <li key={svc.provider} className="flex justify-between items-center border-b border-gray-700 py-3">
                <div>
                  <span className="font-medium text-white">{svc.provider}</span>
                  <span className={`ml-2 text-xs px-2 py-1 rounded-full ${svc.is_active ? 'bg-green-500/10 text-green-400' : 'bg-gray-500/10 text-gray-400'}`}>
                    {svc.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-400 truncate max-w-[200px]">{svc.description}</span>
                  <Button variant="danger" size="sm" onClick={() => handleDelete(svc.provider)}>Delete</Button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Add Connection Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass p-6 rounded-lg shadow">
          <div className="text-4xl mb-4">🗄️</div>
          <h3 className="text-xl font-semibold text-white mb-2">Vector Database</h3>
          <p className="text-slate-400 text-sm mb-4">Embeddings store karne ke liye Qdrant ya MongoDB connect karein.</p>
          <button onClick={() => setWizardType('vector')} className="btn-primary px-4 py-2 rounded-md text-sm text-white">Connect Vector DB</button>
        </div>

        <div className="glass p-6 rounded-lg shadow">
          <div className="text-4xl mb-4">🛒</div>
          <h3 className="text-xl font-semibold text-white mb-2">Data Source (Store)</h3>
          <p className="text-slate-400 text-sm mb-4">Shopify, WooCommerce, ya Custom MongoDB se products fetch karein.</p>
          <button onClick={() => setWizardType('store')} className="btn-primary px-4 py-2 rounded-md text-sm text-white">Connect Store</button>
        </div>
      </div>

      {/* Select Active Vector DB (🔥 Ab sahi kaam karega) */}
      <div className="glass p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-white mb-4">Select Active Vector DB</h3>
        <div className="flex gap-4">
          <select 
            value={selectedProvider} 
            onChange={(e) => setSelectedProvider(e.target.value)}
            className="input-dark block w-1/3 rounded-md border-gray-700 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm"
          >
            <option value="">Select Provider</option>
            {integrations.filter(svc => svc.provider === 'qdrant' || svc.provider === 'mongodb').map((svc) => (
              <option key={svc.provider} value={svc.provider}>{svc.provider}</option>
            ))}
          </select>
          
          <input 
            type="text" 
            placeholder="Collection Name (e.g., visual_search_products)" 
            value={selectedCollection} 
            onChange={(e) => setSelectedCollection(e.target.value)}
            className="input-dark block w-1/2 rounded-md border-gray-700 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm"
          />
          
          <Button onClick={handleSelectVectorDB} variant="primary">Select</Button>
        </div>
      </div>

      {/* Wizard Modal */}
      {wizardType && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-4">
          <div className="bg-dark-800 p-6 rounded-xl w-full max-w-2xl relative">
            <button onClick={() => setWizardType(null)} className="absolute top-4 right-4 text-slate-400 hover:text-white">✕</button>
            {wizardType === 'vector' ? (
              <SetupWizard initialStep={1} onComplete={() => { onIntegrationsChange(); setWizardType(null) }} />
            ) : (
              <SetupWizard initialStep={2} onComplete={() => { onIntegrationsChange(); setWizardType(null) }} />
            )}
          </div>
        </div>
      )}

      {/* API Key Section */}
      <div className="glass p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-white mb-4">Your Integration Keys</h3>
        <ApiKeyDisplay apiKey={apiKey} />
      </div>

      {/* 🔥 NAYA: File Upload Section */}
      <FileUpload />
    </div>
  )
}
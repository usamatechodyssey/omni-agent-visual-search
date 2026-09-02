import { useState } from 'react'
import { SettingsAPI, VisualAPI } from '../../services/api'
import Button from '../ui/Button'
import { useToast } from '../ui/Toast'

// 🔥 Accept initialStep prop (1 = Vector DB, 2 = Store)
export default function SetupWizard({ onComplete, initialStep = 1 }) {
  // 🔥 State ko initialStep se initialize karein
  const [step, setStep] = useState(initialStep)
  const [loading, setLoading] = useState(false)
  const { addToast } = useToast()

  // Vector DB Form State
  const [dbProvider, setDbProvider] = useState('qdrant')
  const [dbUrl, setDbUrl] = useState('')
  const [dbApiKey, setDbApiKey] = useState('')
  const [dbConnectionString, setDbConnectionString] = useState('')
  const [dbName, setDbName] = useState('')
  const [dbCollection, setDbCollection] = useState('visual_search_products')

  // Data Source Form State
  const [sourceType, setSourceType] = useState('shopify')
  const [sourceDetails, setSourceDetails] = useState({})

  const handleConnectVectorDB = async () => {
    setLoading(true)
    try {
      const credentials = {}
      if (dbProvider === 'qdrant') {
        credentials.url = dbUrl
        credentials.api_key = dbApiKey
        credentials.visual_collection_name = dbCollection
      } else if (dbProvider === 'mongodb') {
        credentials.connection_string = dbConnectionString
        credentials.database_name = dbName
        credentials.visual_collection_name = dbCollection
      } else if (dbProvider === 'pinecone') {
        credentials.api_key = dbApiKey
        credentials.environment = dbUrl
        credentials.visual_collection_name = dbCollection
      }

      await SettingsAPI.connectVectorDB(dbProvider, credentials)
      addToast(`${dbProvider} connected successfully!`, 'success')
      setStep(2) // Ab Step 2 par move karein
    } catch (err) {
      addToast(`Error: ${err.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleConnectDataSource = async () => {
    setLoading(true)
    try {
      await SettingsAPI.connectDataSource(sourceType, sourceDetails)
      addToast(`${sourceType} connected successfully!`, 'success')
      setStep(3) // Ab Step 3 par move karein
    } catch (err) {
      addToast(`Error: ${err.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleStartSync = async () => {
    setLoading(true)
    try {
      await SettingsAPI.selectVectorDB(dbProvider, dbCollection)
      await VisualAPI.triggerSync()
      addToast('Visual Sync started!', 'success')
      onComplete()
    } catch (err) {
      addToast(`Error: ${err.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // (Baaki ka JSX exactly same rahega, bas steps dynamically render honge)
  return (
    <div className="glass p-8 rounded-xl max-w-2xl mx-auto mt-8">
      <div className="flex items-center gap-4 mb-8">
        {[1, 2, 3].map((s) => (
          <div key={s} className={`h-2 w-10 rounded-full ${s <= step ? 'bg-cyan-500' : 'bg-slate-700'}`} />
        ))}
      </div>

      {step === 1 && (
        <div>
          <h2 className="text-xl font-bold text-white mb-4">Step 1: Connect Vector DB</h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-slate-400">Provider</label>
              <select value={dbProvider} onChange={(e) => setDbProvider(e.target.value)} className="input-dark w-full mt-1">
                <option value="qdrant">Qdrant</option>
                <option value="mongodb">MongoDB Atlas</option>
                <option value="pinecone">Pinecone</option>
              </select>
            </div>
            
            {dbProvider === 'qdrant' && (
              <>
                <input className="input-dark w-full" placeholder="Cluster URL (https://...)" value={dbUrl} onChange={(e) => setDbUrl(e.target.value)} />
                <input className="input-dark w-full" placeholder="API Key" value={dbApiKey} onChange={(e) => setDbApiKey(e.target.value)} />
              </>
            )}
            {dbProvider === 'mongodb' && (
              <>
                <input className="input-dark w-full" placeholder="Connection String (mongodb+srv://...)" value={dbConnectionString} onChange={(e) => setDbConnectionString(e.target.value)} />
                <input className="input-dark w-full" placeholder="Database Name" value={dbName} onChange={(e) => setDbName(e.target.value)} />
              </>
            )}
            {dbProvider === 'pinecone' && (
              <>
                <input className="input-dark w-full" placeholder="Environment (e.g., us-east-1)" value={dbUrl} onChange={(e) => setDbUrl(e.target.value)} />
                <input className="input-dark w-full" placeholder="API Key" value={dbApiKey} onChange={(e) => setDbApiKey(e.target.value)} />
              </>
            )}

            <input className="input-dark w-full" placeholder="Collection Name" value={dbCollection} onChange={(e) => setDbCollection(e.target.value)} />
            
            <Button onClick={handleConnectVectorDB} disabled={loading} variant="primary" className="w-full">
              {loading ? 'Connecting...' : 'Connect Vector DB'}
            </Button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div>
          <h2 className="text-xl font-bold text-white mb-4">Step 2: Connect Data Source</h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-slate-400">Source Type</label>
              <select value={sourceType} onChange={(e) => setSourceType(e.target.value)} className="input-dark w-full mt-1">
                <option value="shopify">Shopify</option>
                <option value="woocommerce">WooCommerce</option>
                <option value="mongodb_store">MongoDB (Custom DB)</option>
                <option value="sanity">Sanity CMS</option>
              </select>
            </div>

            {sourceType === 'shopify' && (
              <>
                <input className="input-dark w-full" placeholder="Shop URL (e.g., my-store.myshopify.com)" value={sourceDetails.shop_url || ''} onChange={(e) => setSourceDetails({ ...sourceDetails, shop_url: e.target.value })} />
                <input className="input-dark w-full" placeholder="Access Token" value={sourceDetails.access_token || ''} onChange={(e) => setSourceDetails({ ...sourceDetails, access_token: e.target.value })} />
              </>
            )}
            {sourceType === 'woocommerce' && (
              <>
                <input className="input-dark w-full" placeholder="Website URL" value={sourceDetails.url || ''} onChange={(e) => setSourceDetails({ ...sourceDetails, url: e.target.value })} />
                <input className="input-dark w-full" placeholder="Consumer Key" value={sourceDetails.consumer_key || ''} onChange={(e) => setSourceDetails({ ...sourceDetails, consumer_key: e.target.value })} />
                <input className="input-dark w-full" placeholder="Consumer Secret" value={sourceDetails.consumer_secret || ''} onChange={(e) => setSourceDetails({ ...sourceDetails, consumer_secret: e.target.value })} />
              </>
            )}
            {sourceType === 'mongodb_store' && (
              <>
                <input className="input-dark w-full" placeholder="Connection String" value={sourceDetails.connection_string || ''} onChange={(e) => setSourceDetails({ ...sourceDetails, connection_string: e.target.value })} />
                <input className="input-dark w-full" placeholder="Database Name" value={sourceDetails.database_name || ''} onChange={(e) => setSourceDetails({ ...sourceDetails, database_name: e.target.value })} />
                <input className="input-dark w-full" placeholder="Collection Name" value={sourceDetails.collection_name || ''} onChange={(e) => setSourceDetails({ ...sourceDetails, collection_name: e.target.value })} />
              </>
            )}
            {sourceType === 'sanity' && (
              <>
                <input className="input-dark w-full" placeholder="Project ID" value={sourceDetails.project_id || ''} onChange={(e) => setSourceDetails({ ...sourceDetails, project_id: e.target.value })} />
                <input className="input-dark w-full" placeholder="Dataset" value={sourceDetails.dataset || ''} onChange={(e) => setSourceDetails({ ...sourceDetails, dataset: e.target.value })} />
                <input className="input-dark w-full" placeholder="Token" value={sourceDetails.token || ''} onChange={(e) => setSourceDetails({ ...sourceDetails, token: e.target.value })} />
              </>
            )}

            <Button onClick={handleConnectDataSource} disabled={loading} variant="primary" className="w-full">
              {loading ? 'Connecting...' : 'Connect Data Source'}
            </Button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="text-center">
          <h2 className="text-xl font-bold text-white mb-4">Step 3: Ready to Sync!</h2>
          <p className="text-slate-400 mb-6">You have successfully connected your Vector DB and Data Source. Now start syncing your products.</p>
          <Button onClick={handleStartSync} disabled={loading} variant="primary" className="w-full">
            {loading ? 'Starting...' : 'Start Visual Sync'}
          </Button>
        </div>
      )}
    </div>
  )
}
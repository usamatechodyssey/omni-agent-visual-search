import { useState, useEffect } from 'react'
import { IngestionAPI } from '../../services/api'
import Button from '../ui/Button'

export default function JobsHistory() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchJobs = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await IngestionAPI.getJobs()
      setJobs(data || [])
    } catch (err) {
      setError(err.message || 'Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [])

  if (loading) return <div className="text-slate-400 text-center py-4">Loading...</div>
  if (error) return <div className="text-red-400 text-sm">{error}</div>

  return (
    <div className="glass p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-white">Sync History</h3>
        <Button onClick={fetchJobs} variant="ghost" size="sm">
          Refresh
        </Button>
      </div>

      {jobs.length === 0 ? (
        <p className="text-sm text-slate-400">No jobs found.</p>
      ) : (
        <ul className="space-y-3">
          {jobs.map((job) => (
            <li key={job.job_id} className="flex justify-between items-center border-b border-gray-700 py-2">
              <div>
                <p className="text-sm font-medium text-white">
                  {job.ingestion_type} - #{job.job_id}
                </p>
                
                {/* 🔥 YAHAN PRODUCTS AUR IMAGES KA COUNT ALAG-ALAG DIKHAYA */}
                <p className="text-xs text-slate-400 mt-1">
                  Total Products: {job.total_items} | Total Images: {job.details?.total_images || 'N/A'}
                </p>
                <p className="text-xs text-slate-500">
                  Processed Images: {job.items_processed} / {job.details?.total_images || job.total_items}
                </p>
              </div>
              
              <span className={`text-xs px-2 py-1 rounded-full ${
                job.status === 'completed' ? 'bg-green-500/10 text-green-400' :
                job.status === 'processing' ? 'bg-cyan-500/10 text-cyan-400' :
                job.status === 'failed' ? 'bg-red-500/10 text-red-400' : 'bg-slate-500/10 text-slate-400'
              }`}>
                {job.status}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
import { useState } from 'react'
import { FileAPI } from '../../services/api'
import Button from '../ui/Button'
import { useToast } from '../ui/Toast'

export default function FileUpload() {
  const [file, setFile] = useState(null)
  const [headers, setHeaders] = useState([])
  const [mapping, setMapping] = useState({
    title: '',
    slug: '',
    image_url: '',
    product_id: '',
    price: '',
  })
  const [previewLoading, setPreviewLoading] = useState(false)
  const [processLoading, setProcessLoading] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [step, setStep] = useState(1) // 1: Upload, 2: Map Fields, 3: Processed
  const { addToast } = useToast()

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setHeaders([])
      setStep(1)
    }
  }

  const handlePreview = async () => {
    if (!file) {
      addToast('Please select a CSV or JSON file first!', 'error')
      return
    }

    setPreviewLoading(true)
    try {
      const data = await FileAPI.previewFile(file)
      setHeaders(data.headers || [])
      setStep(2)
      addToast('File parsed successfully! Now map your fields.', 'success')
    } catch (err) {
      addToast(`Error: ${err.message}`, 'error')
    } finally {
      setPreviewLoading(false)
    }
  }

  const handleProcess = async () => {
    if (!file || !mapping.title || !mapping.slug || !mapping.image_url) {
      addToast('Please map Title, Slug, and Image URL fields.', 'error')
      return
    }

    setProcessLoading(true)
    try {
      const data = await FileAPI.processFile(file, mapping)
      setJobId(data.job_id)
      setStep(3)
      addToast('File processing started successfully!', 'success')
    } catch (err) {
      addToast(`Error: ${err.message}`, 'error')
    } finally {
      setProcessLoading(false)
    }
  }

  return (
    <div className="glass p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-white mb-4">Upload Product Data (CSV / JSON)</h3>

      {/* Step 1: Upload File */}
      {step === 1 && (
        <div className="space-y-4">
          <label className="flex-1 cursor-pointer border-2 border-dashed border-gray-600 hover:border-cyan-400 rounded-lg p-6 flex flex-col items-center justify-center text-center transition-all">
            <span className="text-3xl mb-2">📁</span>
            <span className="text-sm text-slate-400">
              {file ? file.name : 'Click to upload CSV or JSON file'}
            </span>
            <input type="file" className="hidden" accept=".csv,.json" onChange={handleFileChange} />
          </label>
          <Button onClick={handlePreview} disabled={!file || previewLoading} variant="primary" className="w-full">
            {previewLoading ? 'Analyzing...' : 'Analyze Headers'}
          </Button>
        </div>
      )}

      {/* Step 2: Map Fields */}
      {step === 2 && (
        <div className="space-y-4">
          <p className="text-sm text-slate-400">Please map your CSV/JSON columns to system fields:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-400">Title Field *</label>
              <select className="input-dark w-full mt-1" value={mapping.title} onChange={(e) => setMapping({ ...mapping, title: e.target.value })}>
                <option value="">Select Column</option>
                {headers.map((h) => <option key={h} value={h}>{h}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400">Slug Field *</label>
              <select className="input-dark w-full mt-1" value={mapping.slug} onChange={(e) => setMapping({ ...mapping, slug: e.target.value })}>
                <option value="">Select Column</option>
                {headers.map((h) => <option key={h} value={h}>{h}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400">Image URL Field *</label>
              <select className="input-dark w-full mt-1" value={mapping.image_url} onChange={(e) => setMapping({ ...mapping, image_url: e.target.value })}>
                <option value="">Select Column</option>
                {headers.map((h) => <option key={h} value={h}>{h}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400">Product ID Field</label>
              <select className="input-dark w-full mt-1" value={mapping.product_id} onChange={(e) => setMapping({ ...mapping, product_id: e.target.value })}>
                <option value="">Select Column</option>
                {headers.map((h) => <option key={h} value={h}>{h}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400">Price Field</label>
              <select className="input-dark w-full mt-1" value={mapping.price} onChange={(e) => setMapping({ ...mapping, price: e.target.value })}>
                <option value="">Select Column</option>
                {headers.map((h) => <option key={h} value={h}>{h}</option>)}
              </select>
            </div>
          </div>
          <Button onClick={handleProcess} disabled={processLoading} variant="primary" className="w-full">
            {processLoading ? 'Processing...' : 'Process File'}
          </Button>
        </div>
      )}

      {/* Step 3: Success */}
      {step === 3 && (
        <div className="text-center py-6">
          <div className="text-4xl mb-4">✅</div>
          <h4 className="text-lg font-medium text-white mb-2">Job Started Successfully!</h4>
          <p className="text-sm text-slate-400 mb-4">Job ID: #{jobId}</p>
          <Button variant="ghost" onClick={() => { setStep(1); setFile(null); setHeaders([]); setJobId(null); }}>
            Upload Another File
          </Button>
        </div>
      )}
    </div>
  )
}
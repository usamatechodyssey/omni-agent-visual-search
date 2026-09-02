import { useState } from 'react'
import { useToast } from '../ui/Toast'
import Button from '../ui/Button'

export default function ApiKeyDisplay({ apiKey }) {
  const [showKey, setShowKey] = useState(false)
  const [copied, setCopied] = useState(false)
  const { addToast } = useToast()

  // Copy to clipboard with fallback
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(apiKey)
      setCopied(true)
      addToast('API Key copied to clipboard!', 'success')
      setTimeout(() => setCopied(false), 3000)
    } catch (err) {
      // Fallback for older browsers or insecure contexts
      const textarea = document.createElement('textarea')
      textarea.value = apiKey
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      setCopied(true)
      addToast('API Key copied!', 'success')
      setTimeout(() => setCopied(false), 3000)
    }
  }

  return (
    <div className="glass p-6 rounded-lg shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-white">Your API Key</h3>
        <span className="text-xs px-2 py-1 bg-green-500/10 text-green-400 rounded-full border border-green-500/20">
          🔒 Secret
        </span>
      </div>
      
      <div className="bg-dark-800 rounded-md p-4 flex items-center gap-3">
        <code className="flex-1 text-sm text-cyan-400 truncate">
          {showKey ? apiKey : 'omni_••••••••••••••••••••••••••'}
        </code>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowKey(!showKey)}
          className="text-slate-400 hover:text-white"
        >
          {showKey ? 'Hide' : 'Show'}
        </Button>
        
        <Button
          variant="primary"
          size="sm"
          onClick={handleCopy}
        >
          {copied ? '✓ Copied' : 'Copy'}
        </Button>
      </div>
      
      <p className="mt-3 text-xs text-slate-500">
        This key is used in your widget or API calls. <span className="text-amber-500">Do not share this key publicly.</span>
      </p>
    </div>
  )
}
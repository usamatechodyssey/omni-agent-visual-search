import { useState } from 'react'
import Button from '../ui/Button'
import { useToast } from '../ui/Toast'

export default function WidgetCode({ apiKey }) {
  const [copied, setCopied] = useState(false)
  const { addToast } = useToast()

  // Backend URL (VITE_API_URL se aayega)
  const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

  // Widget Script Code Generate
  const scriptCode = `<script
  data-api-key="${apiKey}"
  data-api-url="${apiUrl}"
  src="${apiUrl}/static/widget.js"
></script>`

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(scriptCode)
      setCopied(true)
      addToast('Widget code copied!', 'success')
      setTimeout(() => setCopied(false), 3000)
    } catch (err) {
      addToast('Failed to copy code', 'error')
    }
  }

  return (
    <div className="glass p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-white">Embeddable Widget Script</h3>
        <Button onClick={handleCopy} variant="primary" size="sm">
          {copied ? '✓ Copied' : 'Copy Code'}
        </Button>
      </div>
      
      <p className="text-sm text-slate-400 mb-3">
        Is code ko apni website ke <code className="text-cyan-400">&lt;head&gt;</code> ya <code className="text-cyan-400">&lt;body&gt;</code> tag mein paste karein. Widget khud load ho jayega!
      </p>
      
      {/* Code Block */}
      <pre className="bg-dark-800 p-4 rounded-md overflow-x-auto text-sm text-cyan-400">
        <code>{scriptCode}</code>
      </pre>
    </div>
  )
}
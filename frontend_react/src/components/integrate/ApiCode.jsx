import { useState } from 'react'
import Button from '../ui/Button'
import { useToast } from '../ui/Toast'

export default function ApiCode({ apiKey }) {
  const [copied, setCopied] = useState(false)
  const { addToast } = useToast()

  const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

  // Fetch API Example Generate
  const fetchCode = `const formData = new FormData();
formData.append('file', imageFile); // imageFile = user ki image

const response = await fetch('${apiUrl}/api/v1/visual/search', {
    method: 'POST',
    headers: {
        'x-api-key': '${apiKey}', // Apni unique API key
    },
    body: formData
});

const data = await response.json();
console.log(data.results); // Matching products`

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(fetchCode)
      setCopied(true)
      addToast('API code copied!', 'success')
      setTimeout(() => setCopied(false), 3000)
    } catch (err) {
      addToast('Failed to copy code', 'error')
    }
  }

  return (
    <div className="glass p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-white">Custom API Integration (JavaScript)</h3>
        <Button onClick={handleCopy} variant="primary" size="sm">
          {copied ? '✓ Copied' : 'Copy Code'}
        </Button>
      </div>
      
      <p className="text-sm text-slate-400 mb-3">
        Agar aap apna khud ka UI banana chahte hain, toh yeh fetch code use karein. Image upload karke results hasil karein.
      </p>
      
      {/* Code Block */}
      <pre className="bg-dark-800 p-4 rounded-md overflow-x-auto text-sm text-cyan-400">
        <code>{fetchCode}</code>
      </pre>
    </div>
  )
}
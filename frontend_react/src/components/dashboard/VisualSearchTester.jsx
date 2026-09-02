import { useState } from 'react'
import { VisualAPI } from '../../services/api'
import Button from '../ui/Button'
import { useToast } from '../ui/Toast'

export default function VisualSearchTester({ apiKey }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState([])
  const [hasSearched, setHasSearched] = useState(false)
  const { addToast } = useToast()

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      setPreviewUrl(URL.createObjectURL(file))
      setResults([])
      setHasSearched(false)
    }
  }

  const handleSearch = async () => {
    if (!selectedFile) {
      addToast('Please select an image first!', 'error')
      return
    }

    setLoading(true)
    setHasSearched(true)

    try {
      const data = await VisualAPI.searchByImage(apiKey, selectedFile)
      if (data.results && data.results.length > 0) {
        setResults(data.results)
        addToast('Search completed successfully!', 'success')
      } else {
        setResults([])
        addToast('No matching products found.', 'info')
      }
    } catch (err) {
      addToast(`Error: ${err.message}`, 'error')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  // 🔥 Copy Slug Function
  const handleCopySlug = async (slug) => {
    try {
      await navigator.clipboard.writeText(slug)
      addToast('Slug copied to clipboard!', 'success')
    } catch (err) {
      addToast('Failed to copy slug', 'error')
    }
  }

  return (
    <div className="glass p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-white mb-4">Live Search Tester</h3>

      {/* Upload & Search Area */}
      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <label className="flex-1 cursor-pointer border-2 border-dashed border-gray-600 hover:border-cyan-400 rounded-lg p-4 flex flex-col items-center justify-center min-h-[140px] transition-all">
          {previewUrl ? (
            <img src={previewUrl} alt="Preview" className="h-24 w-24 object-cover rounded-md" />
          ) : (
            <>
              <span className="text-3xl mb-2">📤</span>
              <span className="text-sm text-slate-400 text-center">Click to upload an image</span>
            </>
          )}
          <input type="file" className="hidden" accept="image/*" onChange={handleImageChange} />
        </label>

        <div className="flex items-center justify-center sm:w-1/3">
          <Button 
            onClick={handleSearch} 
            disabled={!selectedFile || loading} 
            variant="primary"
            className="w-full"
          >
            {loading ? 'Searching...' : '🔍 Search'}
          </Button>
        </div>
      </div>

      {/* Results Grid - Fully Responsive */}
      {hasSearched && !loading && (
        <div className="mt-6">
          {results.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {results.map((item) => (
                <div key={item.id} className="group bg-dark-800 rounded-lg overflow-hidden border border-gray-700 hover:border-cyan-500/50 transition-all hover:shadow-xl hover:shadow-cyan-500/10">
                  {/* Image Container with aspect ratio to prevent stretching */}
                  <div className="relative aspect-square overflow-hidden">
                    <img 
                      src={item.payload?.image_url} 
                      alt={item.payload?.title || 'Product'} 
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      onError={(e) => { e.target.src = 'https://via.placeholder.com/300?text=No+Image' }}
                    />
                    
                    {/* Score Badge (Overlay on Image) */}
                    <div className="absolute top-2 right-2 bg-cyan-500/90 text-white text-xs font-bold px-2 py-1 rounded-full backdrop-blur-sm">
                      {Math.round(item.score * 100)}%
                    </div>
                  </div>

                  {/* Card Content */}
                  <div className="p-3">
                    <p className="text-sm font-medium text-white truncate mb-1" title={item.payload?.title || 'Untitled Product'}>
                      {item.payload?.title || 'Untitled Product'}
                    </p>
                    
                    {/* 🔥 FIX: Blank page ki jagah Slug Copy Button */}
                    {item.payload?.slug && (
                      <button
                        onClick={() => handleCopySlug(item.payload.slug)}
                        className="text-xs text-cyan-400 hover:text-cyan-300 truncate block w-full text-left"
                      >
                        Copy Slug: {item.payload.slug}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400 text-center mt-4">No products found matching this image.</p>
          )}
        </div>
      )}
    </div>
  )
}
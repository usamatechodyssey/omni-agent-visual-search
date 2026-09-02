import { useState } from 'react'
import { X } from 'lucide-react' // Ensure lucide-react is installed: npm install lucide-react

const slides = [
  {
    title: "Welcome to OmniAgent Visual Search",
    description: "Is system se aap apni e-commerce website par AI-powered image search laga sakte hain. Customer image upload karega, system matching products dikhayega.",
    icon: "🔍"
  },
  {
    title: "Step 1: Connect Vector Database",
    description: "Images ke embeddings store karne ke liye database chahiye. Hum Qdrant (Recommended) ya MongoDB Atlas support karte hain. User apni key daal kar connect kar sakta hai.",
    icon: "🗄️"
  },
  {
    title: "Step 2: Connect Your Store",
    description: "Apne products ka data laane ke liye Shopify, WooCommerce, ya Custom MongoDB connect karein. System automatically products ki images fetch karega.",
    icon: "🛒"
  },
  {
    title: "Step 3: Map Your Fields (Custom Format)",
    description: "Agar custom MongoDB use kar rahe hain, toh system puchhega ke aapka 'title', 'slug', aur 'image_url' kis field mein hai. User apna data format khud define karega.",
    icon: "📝"
  },
  {
    title: "Step 4: Sync & Integrate",
    description: "Sync button dabate hi system CLIP model se embeddings banayega. Phir aapko ek 'Widget Code' milega jise apni website par paste kar sakte hain.",
    icon: "🚀"
  },
]

export default function OnboardingGuide({ isOpen, onClose }) {
  const [currentSlide, setCurrentSlide] = useState(0)

  if (!isOpen) return null

  const handleNext = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(currentSlide + 1)
    } else {
      onClose()
    }
  }

  const handlePrevious = () => {
    if (currentSlide > 0) {
      setCurrentSlide(currentSlide - 1)
    }
  }

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="glass w-full max-w-2xl p-8 rounded-2xl relative">
        {/* Close Button */}
        <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-white">
          <X size={24} />
        </button>

        {/* Slide Content */}
        <div className="flex flex-col items-center text-center">
          <div className="text-6xl mb-6">{slides[currentSlide].icon}</div>
          <h2 className="text-2xl font-bold text-white mb-4">{slides[currentSlide].title}</h2>
          <p className="text-slate-300 leading-relaxed">{slides[currentSlide].description}</p>
        </div>

        {/* Navigation Dots */}
        <div className="flex justify-center gap-2 mt-8">
          {slides.map((_, index) => (
            <div
              key={index}
              className={`h-2 w-8 rounded-full transition-all ${
                index === currentSlide ? 'bg-cyan-500' : 'bg-slate-700'
              }`}
            />
          ))}
        </div>

        {/* Buttons */}
        <div className="flex justify-between mt-8">
          <button
            onClick={handlePrevious}
            disabled={currentSlide === 0}
            className="text-slate-400 hover:text-white disabled:opacity-30"
          >
            ← Previous
          </button>
          <button onClick={handleNext} className="btn-primary px-6 py-2 rounded-md text-white">
            {currentSlide === slides.length - 1 ? 'Get Started' : 'Next →'}
          </button>
        </div>
      </div>
    </div>
  )
}
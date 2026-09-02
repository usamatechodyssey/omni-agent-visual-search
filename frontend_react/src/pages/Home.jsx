import { Link } from 'react-router-dom'

// 🔥 isLoggedIn prop accept karta hai
export default function Home({ isLoggedIn }) {
  return (
    <div className="relative isolate overflow-hidden bg-dark-900">
      <div className="mx-auto max-w-7xl px-6 pb-24 pt-10 sm:pb-32 lg:px-8">
        <div className="mx-auto max-w-2xl flex flex-col items-center text-center">
          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl">
            Build Stunning <span className="gradient-text">Visual Search</span> for your E-commerce Store
          </h1>
          <p className="mt-6 text-lg leading-8 text-slate-300">
            OmniAgent Visual Search lets your customers upload an image and instantly find the exact product they're looking for. 100% Free, Open Source, and Cloud-ready.
          </p>
          
          {/* 🔥 Conditional Buttons: Agar logged in hai toh Dashboard, warna Login/Register */}
          <div className="mt-10 flex items-center justify-center gap-x-6">
            {isLoggedIn ? (
              <Link to="/dashboard" className="btn-primary rounded-md px-3.5 py-2.5 text-sm font-semibold text-white">
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn-primary rounded-md px-3.5 py-2.5 text-sm font-semibold text-white">Get Started Free</Link>
                <Link to="/login" className="text-sm font-semibold leading-6 text-cyan-400 hover:text-cyan-300">Login <span aria-hidden="true">→</span></Link>
              </>
            )}
          </div>
        </div>
        
        {/* Placeholder */}
        <div className="mt-16 flow-root">
          <div className="glass p-8 text-center text-slate-400">
            Visual Search Demo Dashboard Will Appear Here
          </div>
        </div>
      </div>
    </div>
  )
}
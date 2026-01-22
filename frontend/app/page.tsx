import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-6xl font-bold mb-4">
          KERN Financial AI
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-Powered Financial Transaction Processing
        </p>
        
        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Login
          </Link>
          <Link
            href="/signup"
            className="px-6 py-3 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition"
          >
            Sign Up
          </Link>
        </div>
        
        <div className="mt-12 max-w-2xl">
          <h2 className="text-2xl font-semibold mb-4">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold mb-2">📄 Smart Document Processing</h3>
              <p className="text-sm text-gray-600">
                Upload bank statements, receipts, and financial documents
              </p>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold mb-2">🤖 AI Classification</h3>
              <p className="text-sm text-gray-600">
                Automatically categorize transactions using Claude AI
              </p>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold mb-2">📊 Financial Reports</h3>
              <p className="text-sm text-gray-600">
                Generate income statements and balance sheets instantly
              </p>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold mb-2">🔍 Review Queue</h3>
              <p className="text-sm text-gray-600">
                Review and approve AI classifications with confidence scores
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

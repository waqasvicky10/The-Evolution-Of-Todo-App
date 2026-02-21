/**
 * Landing page (root /).
 *
 * Public homepage with welcome message and links to login/register.
 * This is the entry point for unauthenticated users.
 */

import Link from "next/link";


export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-2xl mx-auto px-6 text-center">
        {/* Logo/Title */}
        <div className="mb-8">
          <h1 className="text-6xl font-bold text-gray-900 mb-4">
            Todo App
          </h1>
          <p className="text-xl text-gray-600">
            Phase V - Event-Driven Architecture
          </p>
        </div>

        {/* Description */}
        <div className="mb-12">
          <p className="text-lg text-gray-700 mb-4">
            A modern, multi-user todo application with secure authentication
            and persistent storage.
          </p>
          <p className="text-md text-gray-600">
            Keep track of your tasks, mark them complete, and access them
            from anywhere.
          </p>
        </div>

        {/* Features */}
        <div className="mb-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-3">🔒</div>
            <h3 className="font-semibold text-gray-900 mb-2">Secure</h3>
            <p className="text-sm text-gray-600">
              JWT auth, Dapr secrets, Kubernetes
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-3">⚡</div>
            <h3 className="font-semibold text-gray-900 mb-2">Event-Driven</h3>
            <p className="text-sm text-gray-600">
              Dapr + Redpanda for real-time events
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-3">🤖</div>
            <h3 className="font-semibold text-gray-900 mb-2">AI Powered</h3>
            <p className="text-sm text-gray-600">
              Chat agent, voice commands, smart tasks
            </p>
          </div>
        </div>

        {/* Call to Action */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/register"
              className="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 transition duration-200"
            >
              Get Started
            </Link>
            <Link
              href="/login"
              className="px-8 py-3 bg-white text-indigo-600 font-semibold rounded-lg shadow-md hover:bg-gray-50 transition duration-200"
            >
              Sign In
            </Link>
          </div>
          <p className="text-sm text-gray-500">
            Free to use. No credit card required.
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="absolute bottom-6 text-center">
        <p className="text-sm text-gray-500">
          Built with Next.js, FastAPI, and PostgreSQL
        </p>
      </footer>
    </div>
  );
}

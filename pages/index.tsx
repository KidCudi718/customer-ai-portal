import { useState, useEffect } from 'react'
import Head from 'next/head'
import { motion } from 'framer-motion'
import { ChatBubbleLeftRightIcon, PhoneIcon, ChartBarIcon, ShoppingCartIcon } from '@heroicons/react/24/outline'
import LoginModal from '../components/LoginModal'
import CustomerDashboard from '../components/CustomerDashboard'

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [showLogin, setShowLogin] = useState(false)
  const [customer, setCustomer] = useState(null)

  useEffect(() => {
    // Check for existing session
    const token = localStorage.getItem('access_token')
    const customerData = localStorage.getItem('customer_data')
    
    if (token && customerData) {
      setCustomer(JSON.parse(customerData))
      setIsLoggedIn(true)
    }
  }, [])

  const handleLogin = (customerData: any, token: string) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('customer_data', JSON.stringify(customerData))
    setCustomer(customerData)
    setIsLoggedIn(true)
    setShowLogin(false)
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('customer_data')
    setCustomer(null)
    setIsLoggedIn(false)
  }

  if (isLoggedIn && customer) {
    return <CustomerDashboard customer={customer} onLogout={handleLogout} />
  }

  return (
    <>
      <Head>
        <title>Customer AI Portal - Your Personal Electronics Assistant</title>
        <meta name=\"description\" content=\"AI-powered customer service portal for electronics retailers\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <link rel=\"icon\" href=\"/favicon.ico\" />
      </Head>

      <div className=\"min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50\">
        {/* Header */}
        <header className=\"bg-white shadow-sm border-b border-gray-200\">
          <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8\">
            <div className=\"flex justify-between items-center py-6\">
              <div className=\"flex items-center\">
                <div className=\"flex-shrink-0\">
                  <h1 className=\"text-2xl font-bold text-gray-900\">Customer AI Portal</h1>
                </div>
              </div>
              <div className=\"flex items-center space-x-4\">
                <button
                  onClick={() => setShowLogin(true)}
                  className=\"bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors\"
                >
                  Customer Login
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <main className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12\">
          <div className=\"text-center\">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className=\"text-4xl md:text-6xl font-bold text-gray-900 mb-6\">
                Your Personal
                <span className=\"text-blue-600\"> AI Assistant</span>
              </h1>
              <p className=\"text-xl text-gray-600 mb-8 max-w-3xl mx-auto\">
                Get instant access to your complete order history, place new orders, 
                and get expert advice on electronics accessories - all through natural conversation.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className=\"mb-12\"
            >
              <button
                onClick={() => setShowLogin(true)}
                className=\"bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-medium transition-colors shadow-lg hover:shadow-xl\"
              >
                Access Your Account
              </button>
            </motion.div>
          </div>

          {/* Features Grid */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className=\"grid md:grid-cols-2 lg:grid-cols-4 gap-8 mt-16\"
          >
            <FeatureCard
              icon={<ChatBubbleLeftRightIcon className=\"h-8 w-8\" />}
              title=\"AI Chat Support\"
              description=\"Talk naturally about your needs. Our AI knows your complete history and preferences.\"
            />
            <FeatureCard
              icon={<ShoppingCartIcon className=\"h-8 w-8\" />}
              title=\"Instant Reordering\"
              description=\"Reorder your favorite products with a simple message. No browsing required.\"
            />
            <FeatureCard
              icon={<PhoneIcon className=\"h-8 w-8\" />}
              title=\"Voice Assistant\"
              description=\"Speak with our AI avatar for hands-free ordering and support.\"
            />
            <FeatureCard
              icon={<ChartBarIcon className=\"h-8 w-8\" />}
              title=\"Purchase Analytics\"
              description=\"View your spending patterns, favorite products, and personalized recommendations.\"
            />
          </motion.div>

          {/* Demo Section */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className=\"mt-20 bg-white rounded-2xl shadow-xl p-8\"
          >
            <h2 className=\"text-3xl font-bold text-center text-gray-900 mb-8\">
              See It In Action
            </h2>
            <div className=\"grid md:grid-cols-2 gap-8 items-center\">
              <div>
                <h3 className=\"text-xl font-semibold text-gray-900 mb-4\">
                  Natural Conversation
                </h3>
                <div className=\"space-y-4\">
                  <ChatBubble
                    message=\"Hi! I need to reorder those iPhone 15 cases I bought last month\"
                    isUser={true}
                  />
                  <ChatBubble
                    message=\"I found your order from October 15th - 50x iPhone 15 Pro Clear Cases at $12.99 each. Would you like to reorder the same quantity?\"
                    isUser={false}
                  />
                  <ChatBubble
                    message=\"Yes, but make it 75 this time\"
                    isUser={true}
                  />
                  <ChatBubble
                    message=\"Perfect! I've created order #ORD-A7B9C2D1 for 75x iPhone 15 Pro Clear Cases. Total: $974.25. Estimated delivery: 3-5 business days.\"
                    isUser={false}
                  />
                </div>
              </div>
              <div className=\"bg-gray-50 rounded-lg p-6\">
                <h3 className=\"text-xl font-semibold text-gray-900 mb-4\">
                  What You Can Do
                </h3>
                <ul className=\"space-y-3 text-gray-600\">
                  <li className=\"flex items-center\">
                    <span className=\"w-2 h-2 bg-blue-600 rounded-full mr-3\"></span>
                    View complete order history since day one
                  </li>
                  <li className=\"flex items-center\">
                    <span className=\"w-2 h-2 bg-blue-600 rounded-full mr-3\"></span>
                    Get product compatibility advice
                  </li>
                  <li className=\"flex items-center\">
                    <span className=\"w-2 h-2 bg-blue-600 rounded-full mr-3\"></span>
                    Track orders and shipments
                  </li>
                  <li className=\"flex items-center\">
                    <span className=\"w-2 h-2 bg-blue-600 rounded-full mr-3\"></span>
                    Place new orders conversationally
                  </li>
                  <li className=\"flex items-center\">
                    <span className=\"w-2 h-2 bg-blue-600 rounded-full mr-3\"></span>
                    Get personalized recommendations
                  </li>
                </ul>
              </div>
            </div>
          </motion.div>
        </main>

        {/* Login Modal */}
        {showLogin && (
          <LoginModal
            onClose={() => setShowLogin(false)}
            onLogin={handleLogin}
          />
        )}
      </div>
    </>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className=\"bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow\">
      <div className=\"text-blue-600 mb-4\">{icon}</div>
      <h3 className=\"text-xl font-semibold text-gray-900 mb-2\">{title}</h3>
      <p className=\"text-gray-600\">{description}</p>
    </div>
  )
}

function ChatBubble({ message, isUser }: { message: string, isUser: boolean }) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
        isUser 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-200 text-gray-900'
      }`}>
        <p className=\"text-sm\">{message}</p>
      </div>
    </div>
  )
}
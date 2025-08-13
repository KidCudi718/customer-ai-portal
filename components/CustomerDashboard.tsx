import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChatBubbleLeftRightIcon, 
  MicrophoneIcon, 
  PaperAirplaneIcon,
  ChartBarIcon,
  ShoppingBagIcon,
  ClockIcon,
  UserCircleIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline'
import ChatInterface from './ChatInterface'
import OrderHistory from './OrderHistory'
import Analytics from './Analytics'
import VoiceInterface from './VoiceInterface'

interface Customer {
  id: string
  company_name: string
  email: string
  total_spent: number
  last_order_date: string
}

interface CustomerDashboardProps {
  customer: Customer
  onLogout: () => void
}

export default function CustomerDashboard({ customer, onLogout }: CustomerDashboardProps) {
  const [activeTab, setActiveTab] = useState('chat')
  const [isVoiceMode, setIsVoiceMode] = useState(false)

  const tabs = [
    { id: 'chat', name: 'AI Assistant', icon: ChatBubbleLeftRightIcon },
    { id: 'orders', name: 'Order History', icon: ShoppingBagIcon },
    { id: 'analytics', name: 'Analytics', icon: ChartBarIcon },
  ]

  return (
    <div className=\"min-h-screen bg-gray-50\">
      {/* Header */}
      <header className=\"bg-white shadow-sm border-b border-gray-200\">
        <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8\">
          <div className=\"flex justify-between items-center py-4\">
            <div className=\"flex items-center space-x-4\">
              <h1 className=\"text-xl font-bold text-gray-900\">Customer Portal</h1>
              <div className=\"hidden md:flex items-center space-x-2 text-sm text-gray-600\">
                <UserCircleIcon className=\"h-4 w-4\" />
                <span>{customer.company_name}</span>
              </div>
            </div>
            
            <div className=\"flex items-center space-x-4\">
              {/* Voice Mode Toggle */}
              <button
                onClick={() => setIsVoiceMode(!isVoiceMode)}
                className={`p-2 rounded-lg transition-colors ${
                  isVoiceMode 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                title=\"Toggle Voice Mode\"
              >
                <MicrophoneIcon className=\"h-5 w-5\" />
              </button>
              
              {/* Settings */}
              <button className=\"p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200\">
                <Cog6ToothIcon className=\"h-5 w-5\" />
              </button>
              
              {/* Logout */}
              <button
                onClick={onLogout}
                className=\"px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900\"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Customer Info Bar */}
      <div className=\"bg-blue-50 border-b border-blue-200\">
        <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3\">
          <div className=\"flex items-center justify-between\">
            <div className=\"flex items-center space-x-6 text-sm\">
              <div className=\"flex items-center space-x-2\">
                <span className=\"font-medium text-blue-900\">Total Spent:</span>
                <span className=\"text-blue-700\">${customer.total_spent.toLocaleString()}</span>
              </div>
              <div className=\"flex items-center space-x-2\">
                <ClockIcon className=\"h-4 w-4 text-blue-600\" />
                <span className=\"font-medium text-blue-900\">Last Order:</span>
                <span className=\"text-blue-700\">{new Date(customer.last_order_date).toLocaleDateString()}</span>
              </div>
            </div>
            <div className=\"text-sm text-blue-700\">
              Customer ID: {customer.id}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className=\"bg-white border-b border-gray-200\">
        <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8\">
          <nav className=\"flex space-x-8\" aria-label=\"Tabs\">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className=\"h-5 w-5\" />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8\">
        <AnimatePresence mode=\"wait\">
          {activeTab === 'chat' && (
            <motion.div
              key=\"chat\"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {isVoiceMode ? (
                <VoiceInterface customer={customer} />
              ) : (
                <ChatInterface customer={customer} />
              )}
            </motion.div>
          )}
          
          {activeTab === 'orders' && (
            <motion.div
              key=\"orders\"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <OrderHistory customer={customer} />
            </motion.div>
          )}
          
          {activeTab === 'analytics' && (
            <motion.div
              key=\"analytics\"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Analytics customer={customer} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Quick Actions Floating Button */}
      <div className=\"fixed bottom-6 right-6\">
        <div className=\"flex flex-col space-y-3\">
          {/* Quick Reorder */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className=\"bg-green-600 hover:bg-green-700 text-white p-3 rounded-full shadow-lg\"
            title=\"Quick Reorder\"
          >
            <ShoppingBagIcon className=\"h-6 w-6\" />
          </motion.button>
          
          {/* Emergency Support */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className=\"bg-red-600 hover:bg-red-700 text-white p-3 rounded-full shadow-lg\"
            title=\"Emergency Support\"
          >
            <ChatBubbleLeftRightIcon className=\"h-6 w-6\" />
          </motion.button>
        </div>
      </div>
    </div>
  )
}
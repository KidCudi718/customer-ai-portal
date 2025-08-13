import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { PaperAirplaneIcon, MicrophoneIcon, StopIcon } from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'

interface Message {
  id: string
  text: string
  isUser: boolean
  timestamp: Date
  action?: any
}

interface Customer {
  id: string
  company_name: string
  email: string
}

interface ChatInterfaceProps {
  customer: Customer
}

export default function ChatInterface({ customer }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: `Hello ${customer.company_name}! I'm your AI assistant. I have access to your complete order history and can help you with reorders, product questions, tracking, and recommendations. What can I help you with today?`,
      isUser: false,
      timestamp: new Date()
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      isUser: true,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setIsLoading(true)

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: text.trim(),
          customer_id: customer.id
        })
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.text,
        isUser: false,
        timestamp: new Date(),
        action: data.action
      }

      setMessages(prev => [...prev, aiMessage])

      // Handle actions
      if (data.action) {
        handleAction(data.action)
      }

    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message. Please try again.')
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'I apologize, but I\\'m experiencing technical difficulties. Please try again or contact our support team.',
        isUser: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleAction = (action: any) => {
    switch (action.type) {
      case 'create_order':
        toast.success('Order action detected! Processing...')
        break
      case 'track_order':
        toast.success('Fetching tracking information...')
        break
      case 'product_inquiry':
        toast.success('Looking up product information...')
        break
      default:
        break
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(inputText)
  }

  const startVoiceRecognition = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Voice recognition not supported in this browser')
      return
    }

    const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition
    const recognition = new SpeechRecognition()
    
    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      setIsListening(true)
      toast.success('Listening... Speak now!')
    }

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setInputText(transcript)
      setIsListening(false)
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setIsListening(false)
      toast.error('Voice recognition failed. Please try again.')
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    recognition.start()
  }

  const stopVoiceRecognition = () => {
    setIsListening(false)
  }

  return (
    <div className=\"flex flex-col h-[calc(100vh-300px)] bg-white rounded-lg shadow-lg\">
      {/* Chat Header */}
      <div className=\"flex items-center justify-between p-4 border-b border-gray-200\">
        <div>
          <h2 className=\"text-lg font-semibold text-gray-900\">AI Assistant</h2>
          <p className=\"text-sm text-gray-600\">Ask me anything about your orders, products, or account</p>
        </div>
        <div className=\"flex items-center space-x-2\">
          <div className=\"flex items-center space-x-1\">
            <div className=\"w-2 h-2 bg-green-500 rounded-full animate-pulse\"></div>
            <span className=\"text-sm text-gray-600\">Online</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className=\"flex-1 overflow-y-auto p-4 space-y-4\">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg ${
                message.isUser
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}>
                <p className=\"text-sm whitespace-pre-wrap\">{message.text}</p>
                <p className={`text-xs mt-1 ${
                  message.isUser ? 'text-blue-200' : 'text-gray-500'
                }`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
                
                {/* Action Indicators */}
                {message.action && (
                  <div className=\"mt-2 p-2 bg-blue-50 rounded text-xs text-blue-800\">
                    Action: {message.action.type.replace('_', ' ').toUpperCase()}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {/* Loading Indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className=\"flex justify-start\"
          >
            <div className=\"bg-gray-100 px-4 py-3 rounded-lg\">
              <div className=\"flex items-center space-x-2\">
                <div className=\"flex space-x-1\">
                  <div className=\"w-2 h-2 bg-gray-400 rounded-full animate-bounce\"></div>
                  <div className=\"w-2 h-2 bg-gray-400 rounded-full animate-bounce\" style={{ animationDelay: '0.1s' }}></div>
                  <div className=\"w-2 h-2 bg-gray-400 rounded-full animate-bounce\" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className=\"text-sm text-gray-600\">AI is thinking...</span>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className=\"border-t border-gray-200 p-4\">
        <form onSubmit={handleSubmit} className=\"flex items-center space-x-2\">
          <div className=\"flex-1 relative\">
            <input
              ref={inputRef}
              type=\"text\"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder=\"Type your message... (e.g., 'Show me my last order' or 'I need 50 iPhone cases')\"
              className=\"w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent\"
              disabled={isLoading}
            />
            {isListening && (
              <div className=\"absolute right-3 top-1/2 transform -translate-y-1/2\">
                <div className=\"w-3 h-3 bg-red-500 rounded-full animate-pulse\"></div>
              </div>
            )}
          </div>
          
          {/* Voice Button */}
          <button
            type=\"button\"
            onClick={isListening ? stopVoiceRecognition : startVoiceRecognition}
            className={`p-3 rounded-lg transition-colors ${
              isListening
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
            }`}
            disabled={isLoading}
          >
            {isListening ? (
              <StopIcon className=\"h-5 w-5\" />
            ) : (
              <MicrophoneIcon className=\"h-5 w-5\" />
            )}
          </button>
          
          {/* Send Button */}
          <button
            type=\"submit\"
            disabled={!inputText.trim() || isLoading}
            className=\"bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white p-3 rounded-lg transition-colors\"
          >
            <PaperAirplaneIcon className=\"h-5 w-5\" />
          </button>
        </form>
        
        {/* Quick Actions */}
        <div className=\"flex flex-wrap gap-2 mt-3\">
          {[
            'Show my recent orders',
            'Reorder my last purchase',
            'What iPhone cases do you have?',
            'Track my latest order',
            'Show my spending this year'
          ].map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => sendMessage(suggestion)}
              disabled={isLoading}
              className=\"px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors disabled:opacity-50\"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

// Extend Window interface for speech recognition
declare global {
  interface Window {
    webkitSpeechRecognition: any
    SpeechRecognition: any
  }
}
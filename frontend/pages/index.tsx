import { useState } from 'react'
import axios from 'axios'
import styles from '../styles/Home.module.css'
import { ServiceGuide, ChatResponse } from '../types/chat'
import { EnhancedServiceGuide } from '../src/types/service'
import ServiceGuideDisplay from '../components/ServiceGuideDisplay'
import { EnhancedServiceGuideDisplay } from '../src/components/EnhancedServiceGuideDisplay'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

interface Message {
  role: 'user' | 'assistant'
  content: string
  serviceGuide?: ServiceGuide
  enhancedServiceGuide?: EnhancedServiceGuide
  errorType?: string
  suggestions?: string[]
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post(`${API_URL}/api/v1/chat/`, {
        message: input,
        language: 'en'
      })

      const data: ChatResponse = response.data

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.message,
        serviceGuide: data.service_guide,
        enhancedServiceGuide: data.enhanced_service_guide
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      
      // Handle different types of errors
      let errorMessage = 'Sorry, I encountered an error. Please try again.'
      let errorType = 'system_error'
      let suggestions: string[] = []

      if (axios.isAxiosError(error) && error.response?.data) {
        const errorData = error.response.data
        if (errorData.error_type) {
          errorType = errorData.error_type
          errorMessage = errorData.message || errorMessage
          suggestions = errorData.suggestions || []
        }
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: errorMessage,
        errorType,
        suggestions
      }
      setMessages(prev => [...prev, assistantMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Government Services Assistant</h1>
        <p>Your AI-powered guide for government services</p>
      </header>

      <main className={styles.main}>
        <div className={styles.chatContainer}>
          <div className={styles.messages}>
            {messages.length === 0 && (
              <div className={styles.welcomeMessage}>
                <h2>Welcome! 👋</h2>
                <p>I can help you with:</p>
                <ul>
                  <li>Aadhaar name changes</li>
                  <li>Data access requests</li>
                  <li>Service status tracking</li>
                  <li>Document requirements</li>
                </ul>
                <p>Ask me anything to get started!</p>
              </div>
            )}
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`${styles.message} ${
                  msg.role === 'user' ? styles.userMessage : styles.assistantMessage
                }`}
              >
                <div className={styles.messageContent}>{msg.content}</div>
                {msg.enhancedServiceGuide && (
                  <EnhancedServiceGuideDisplay guide={msg.enhancedServiceGuide} />
                )}
                {msg.serviceGuide && !msg.enhancedServiceGuide && (
                  <ServiceGuideDisplay guide={msg.serviceGuide} />
                )}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className={styles.suggestions}>
                    <h4>Suggestions:</h4>
                    <ul>
                      {msg.suggestions.map((suggestion, idx) => (
                        <li key={idx}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className={`${styles.message} ${styles.assistantMessage}`}>
                <div className={styles.messageContent}>Thinking...</div>
              </div>
            )}
          </div>

          <div className={styles.inputContainer}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask about government services..."
              className={styles.input}
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className={styles.sendButton}
            >
              Send
            </button>
          </div>
        </div>
      </main>

      <footer className={styles.footer}>
        <p>
          ⚠️ This is a guidance system only. Always verify information on official government portals.
        </p>
      </footer>
    </div>
  )
}

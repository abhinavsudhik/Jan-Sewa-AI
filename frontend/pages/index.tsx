import { useState } from 'react'
import axios from 'axios'
import styles from '../styles/Home.module.css'
import { ServiceGuide } from '../types/chat'
import ServiceGuideDisplay from '../components/ServiceGuideDisplay'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Message {
  role: 'user' | 'assistant'
  content: string
  serviceGuide?: ServiceGuide
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

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.message,
        serviceGuide: response.data.service_guide
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }
      setMessages(prev => [...prev, errorMessage])
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
                {msg.serviceGuide && (
                  <ServiceGuideDisplay guide={msg.serviceGuide} />
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

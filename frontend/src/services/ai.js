import api from './api'

export const aiService = {
  // Send a message to the AI chatbot
  async sendMessage(message) {
    try {
      const response = await api.post('/ai/chat/', { message })
      return response
    } catch (error) {
      console.error('AI Chat error:', error)
      throw error
    }
  },

  // Get chat history
  async getChatHistory() {
    try {
      const response = await api.get('/ai/history/')
      return response
    } catch (error) {
      console.error('Get chat history error:', error)
      throw error
    }
  },

  // Clear chat history
  async clearChatHistory() {
    try {
      const response = await api.delete('/ai/clear/')
      return response
    } catch (error) {
      console.error('Clear chat history error:', error)
      throw error
    }
  }
}
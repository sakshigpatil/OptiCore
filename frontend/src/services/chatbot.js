import api from './api';

export const chatbotService = {
  // Conversation endpoints
  getConversations: async () => {
    const response = await api.get('/chatbot/conversations/');
    return response;
  },

  getConversation: async (id) => {
    const response = await api.get(`/chatbot/conversations/${id}/`);
    return response;
  },

  createConversation: async (data) => {
    const response = await api.post('/chatbot/conversations/', data);
    return response;
  },

  deleteConversation: async (id) => {
    await api.delete(`/chatbot/conversations/${id}/`);
  },

  sendMessage: async (conversationId, message) => {
    const response = await api.post(`/chatbot/conversations/${conversationId}/send_message/`, {
      message
    });
    return response;
  },

  markConversationRead: async (conversationId) => {
    const response = await api.post(`/chatbot/conversations/${conversationId}/mark_read/`);
    return response;
  },

  getQuickActions: async () => {
    const response = await api.get('/chatbot/conversations/quick_actions/');
    return response;
  },

  // Message endpoints
  getUnreadCount: async () => {
    const response = await api.get('/chatbot/messages/unread_count/');
    return response;
  },

  // Knowledge base endpoints
  searchKnowledge: async (query, category = '') => {
    const response = await api.get('/chatbot/knowledge/search/', {
      params: { q: query, category }
    });
    return response;
  }
};

export default chatbotService;

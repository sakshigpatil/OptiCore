import React, { useState, useEffect, useRef } from 'react';
import {
  XMarkIcon,
  PaperAirplaneIcon,
  ChatBubbleLeftRightIcon,
  SparklesIcon,
  TrashIcon,
  PlusIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon
} from '@heroicons/react/24/outline';
import { ChatBubbleLeftEllipsisIcon } from '@heroicons/react/24/solid';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import chatbotService from '../../services/chatbot';

const Chatbot = ({ isOpen, onClose }) => {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [quickActions, setQuickActions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [panelWidth, setPanelWidth] = useState(900);
  const [panelHeight, setPanelHeight] = useState(600);
  const [isResizing, setIsResizing] = useState(false);
  const messagesEndRef = useRef(null);
  const resizeStartRef = useRef({ x: 0, width: 0 });

  useEffect(() => {
    if (isOpen) {
      initializeChatbot();
    }
  }, [isOpen]);

  const initializeChatbot = async () => {
    setIsInitializing(true);
    try {
      await Promise.all([
        loadConversations(),
        loadQuickActions()
      ]);
    } catch (error) {
      console.error('Error initializing chatbot:', error);
    } finally {
      setIsInitializing(false);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async (skipAutoLoad = false) => {
    try {
      const data = await chatbotService.getConversations();
      // Handle both array and paginated response
      const conversationList = Array.isArray(data) ? data : (data?.results || []);
      setConversations(conversationList);
      
      // Load first conversation if exists (only on initial load)
      if (!skipAutoLoad && conversationList.length > 0 && !activeConversation) {
        loadConversation(conversationList[0].id);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
      // Don't show error toast on initial load
      setConversations([]);
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      setIsLoading(true);
      const data = await chatbotService.getConversation(conversationId);
      setActiveConversation(data);
      setMessages(data.messages || []);
      
      // Mark as read
      await chatbotService.markConversationRead(conversationId);
    } catch (error) {
      console.error('Error loading conversation:', error);
      toast.error('Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  };

  const loadQuickActions = async () => {
    try {
      const actions = await chatbotService.getQuickActions();
      // Ensure actions is an array
      const actionList = Array.isArray(actions) ? actions : [];
      setQuickActions(actionList);
    } catch (error) {
      console.error('Error loading quick actions:', error);
      // Set default quick actions if API fails
      setQuickActions([
        { id: 'help', label: '❓ Help', message: 'What can you do?' }
      ]);
    }
  };

  const createNewConversation = async () => {
    try {
      const newConv = await chatbotService.createConversation({
        title: 'New Conversation'
      });
      
      // Set new conversation as active with empty messages
      setActiveConversation(newConv);
      setMessages([]);
      
      // Update conversations list without auto-loading
      await loadConversations(true);
      
      toast.success('New chat started!');
    } catch (error) {
      console.error('Error creating conversation:', error);
      toast.error('Failed to create conversation');
    }
  };

  const handleSendMessage = async (text = inputMessage) => {
    if (!text.trim()) return;

    let conversationToUse = activeConversation;

    // Create conversation if none exists
    if (!conversationToUse) {
      try {
        const newConv = await chatbotService.createConversation({
          title: text.substring(0, 50)
        });
        console.log('Created conversation:', newConv);
        
        if (!newConv || !newConv.id) {
          toast.error('Invalid conversation created');
          return;
        }
        
        conversationToUse = newConv;
        setActiveConversation(newConv);
        setConversations([newConv, ...(conversations || [])]);
      } catch (error) {
        console.error('Error creating conversation:', error);
        toast.error('Failed to create conversation');
        return;
      }
    }

    if (!conversationToUse || !conversationToUse.id) {
      toast.error('No active conversation');
      return;
    }

    try {
      setIsSending(true);
      const response = await chatbotService.sendMessage(conversationToUse.id, text);
      
      // Add both user and bot messages
      setMessages([...(messages || []), response.user_message, response.bot_message]);
      setInputMessage('');
      
      // Reload conversations to update last message (skip auto-load)
      loadConversations(true);
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
    } finally {
      setIsSending(false);
    }
  };

  const handleQuickAction = (action) => {
    setInputMessage(action.message);
    handleSendMessage(action.message);
  };

  const handleDeleteConversation = async (conversationId, e) => {
    e.stopPropagation();
    
    if (!window.confirm('Are you sure you want to delete this conversation?')) {
      return;
    }

    try {
      await chatbotService.deleteConversation(conversationId);
      setConversations((conversations || []).filter(c => c.id !== conversationId));
      
      if (activeConversation?.id === conversationId) {
        setActiveConversation(null);
        setMessages([]);
      }
      
      toast.success('Conversation deleted');
    } catch (error) {
      console.error('Error deleting conversation:', error);
      toast.error('Failed to delete conversation');
    }
  };

  const formatTime = (timestamp) => {
    try {
      return format(new Date(timestamp), 'h:mm a');
    } catch {
      return '';
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handleResizeStart = (e) => {
    e.preventDefault();
    setIsResizing(true);
    resizeStartRef.current = {
      x: e.clientX,
      width: panelWidth
    };
  };

  useEffect(() => {
    const handleResizeMove = (e) => {
      if (!isResizing) return;
      
      const deltaX = resizeStartRef.current.x - e.clientX;
      const newWidth = Math.min(
        Math.max(600, resizeStartRef.current.width + deltaX),
        window.innerWidth - 100
      );
      setPanelWidth(newWidth);
    };

    const handleResizeEnd = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleResizeMove);
      document.addEventListener('mouseup', handleResizeEnd);
      document.body.style.cursor = 'ew-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleResizeMove);
      document.removeEventListener('mouseup', handleResizeEnd);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  if (!isOpen) return null;

  if (isInitializing) {
    return (
      <div 
        className="fixed z-50 flex flex-col bg-white shadow-2xl border border-gray-200 overflow-hidden"
        style={isFullscreen ? { 
          top: '1rem',
          left: '1rem',
          right: '1rem',
          bottom: '1rem',
          width: 'calc(100vw - 2rem)',
          height: 'calc(100vh - 2rem)',
          borderRadius: '0.5rem'
        } : { 
          bottom: '1rem',
          right: '1rem',
          width: `min(${panelWidth}px, calc(100vw - 2rem))`, 
          height: `min(${panelHeight}px, calc(100vh - 2rem))`,
          borderRadius: '1rem'
        }}
      >
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Initializing HR Assistant...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="fixed z-50 flex flex-col bg-white shadow-2xl border border-gray-200 overflow-hidden"
      style={isFullscreen ? { 
        top: '1rem',
        left: '1rem',
        right: '1rem',
        bottom: '1rem',
        width: 'calc(100vw - 2rem)',
        height: 'calc(100vh - 2rem)',
        borderRadius: '0.5rem'
      } : { 
        bottom: '1rem',
        right: '1rem',
        width: `min(${panelWidth}px, calc(100vw - 2rem))`, 
        height: `min(${panelHeight}px, calc(100vh - 2rem))`,
        borderRadius: '1rem'
      }}
    >
      {/* Resize Handle */}
      {!isFullscreen && (
        <div
          onMouseDown={handleResizeStart}
          className="absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-indigo-400 transition-colors group"
        >
          <div className="absolute left-0 top-0 bottom-0 w-2 -translate-x-1/2"></div>
        </div>
      )}
      
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-white/20 p-2 rounded-lg">
            <SparklesIcon className="h-6 w-6" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">HR Assistant</h3>
            <p className="text-sm text-indigo-100">Ask me anything about HR operations</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleFullscreen}
            className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors"
            title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
          >
            {isFullscreen ? (
              <ArrowsPointingInIcon className="h-5 w-5" />
            ) : (
              <ArrowsPointingOutIcon className="h-5 w-5" />
            )}
          </button>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Conversations Sidebar */}
        <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col">
          <div className="p-3 border-b border-gray-200">
            <button
              onClick={createNewConversation}
              className="w-full flex items-center justify-center space-x-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <PlusIcon className="h-5 w-5" />
              <span>New Chat</span>
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            {!conversations || conversations.length === 0 ? (
              <div className="p-4 text-center text-gray-500 text-sm">
                No conversations yet
              </div>
            ) : (
              Array.isArray(conversations) && conversations.filter(conv => conv && conv.id).map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => loadConversation(conv.id)}
                  className={`p-3 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors group ${
                    activeConversation?.id === conv.id ? 'bg-indigo-50 border-l-4 border-l-indigo-600' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <ChatBubbleLeftEllipsisIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {conv.title}
                        </p>
                      </div>
                      {conv.last_message && (
                        <p className="text-xs text-gray-500 mt-1 truncate">
                          {conv.last_message.message}
                        </p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">
                        {conv.message_count} messages
                      </p>
                    </div>
                    <button
                      onClick={(e) => handleDeleteConversation(conv.id, e)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-all"
                    >
                      <TrashIcon className="h-4 w-4 text-red-600" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {isLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <ChatBubbleLeftRightIcon className="h-16 w-16 text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Start a Conversation</h3>
                <p className="text-gray-500 mb-6">Ask me anything about HR operations, employees, leaves, or attendance</p>
                
                {/* Quick Actions */}
                {quickActions && quickActions.length > 0 && (
                  <div className="grid grid-cols-2 gap-2 max-w-md">
                    {Array.isArray(quickActions) && quickActions.map((action) => (
                      <button
                        key={action.id}
                        onClick={() => handleQuickAction(action)}
                        className="px-4 py-3 bg-white border border-gray-200 rounded-lg hover:border-indigo-300 hover:bg-indigo-50 transition-colors text-sm text-left"
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <>
                {Array.isArray(messages) && messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.sender === 'USER' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                        msg.sender === 'USER'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-white border border-gray-200 text-gray-900'
                      }`}
                    >
                      <div className="whitespace-pre-wrap break-words">{msg.message}</div>
                      <div className={`text-xs mt-2 ${msg.sender === 'USER' ? 'text-indigo-200' : 'text-gray-400'}`}>
                        {formatTime(msg.created_at)}
                      </div>
                      
                      {/* Suggestions */}
                      {msg.metadata?.suggestions && msg.sender === 'BOT' && (
                        <div className="mt-3 space-y-1">
                          {msg.metadata.suggestions.map((suggestion, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleSendMessage(suggestion)}
                              className="block w-full text-left text-sm px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4 bg-white">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center space-x-2"
            >
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message..."
                disabled={isSending}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isSending}
                className="bg-indigo-600 text-white p-3 rounded-xl hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {isSending ? (
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                ) : (
                  <PaperAirplaneIcon className="h-6 w-6" />
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;

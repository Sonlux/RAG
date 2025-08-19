import React, { useState, useEffect, useRef } from "react";
import { useParams, Link, useLocation, useNavigate } from "react-router-dom";
import {
  Send,
  ArrowLeft,
  User,
  Bot,
  AlertCircle,
  MessageCircle,
  Clock,
} from "lucide-react";

const API_BASE = "http://localhost:8000";

interface Message {
  id: string;
  type: "user" | "assistant" | "error";
  content: string;
  timestamp: string;
  sources?: { pdf: string; page: number }[];
}

interface Session {
  id: string;
  library: string;
  last_updated: string | null;
}

const Chat = () => {
  const { libraryId: chatId } = useParams<{ libraryId: string }>(); // chatId is now the session id
  const location = useLocation();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  // Removed sessionList state as it's no longer needed
  // Removed selectedSession state as it's no longer needed
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get library name and pdf name from query params
  const params = new URLSearchParams(location.search);
  const libraryName = params.get("library") || "";
  const mode = params.get("mode"); // "library" for library mode
  const pdfName = params.get("pdf"); // PDF name for single PDF mode
  
  // Determine chat mode and display info
  const isLibraryMode = mode === "library" || (!pdfName && !mode);
  const chatMode = isLibraryMode ? "library" : "single_pdf";
  const displayTitle = isLibraryMode ? "Entire Library" : pdfName || libraryName;

  useEffect(() => {
    if (chatId) {
      fetchHistory();
    }
    // Removed fetchSessions() call as it's no longer needed
    // eslint-disable-next-line
  }, [chatId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchHistory = async () => {
    setLoading(true);
    try {
      // Get the original ID if available, otherwise use the current chat ID
      const originalId = params.get("original_id") || chatId;
      
      // Include pdf_name as a query parameter if available
      const url =
        pdfName && pdfName !== libraryName
          ? `${API_BASE}/history/${originalId}?pdf_name=${encodeURIComponent(
              pdfName
            )}`
          : `${API_BASE}/history/${originalId}`;

      const res = await fetch(url);

      // Parse the response even if it's not OK, as our backend now returns {"history": []} instead of an error
      const data = await res.json();

      if (Array.isArray(data.history)) {
        if (data.history.length > 0) {
          setMessages(
            data.history
              .map(
                (
                  item: {
                    question: string;
                    answer: string;
                    timestamp?: string;
                  },
                  idx: number
                ) => [
                  {
                    id: `${idx}-q`,
                    type: "user",
                    content: item.question,
                    timestamp: item.timestamp || new Date().toISOString(),
                  },
                  {
                    id: `${idx}-a`,
                    type: "assistant",
                    content: item.answer,
                    timestamp: item.timestamp || new Date().toISOString(),
                  },
                ]
              )
              .flat()
          );
        } else {
          // No history found, but not an error
          setMessages([]);
        }
      } else {
        // Invalid response format
        setMessages([]);
      }
    } catch (error) {
      console.error("Error fetching chat history:", error);
      setMessages([
        {
          id: "error",
          type: "error",
          content:
            "Failed to load chat history. You can start a new conversation.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Removed fetchSessions function as it's no longer needed
  // Removed handleSelectSession function as it's no longer needed

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !chatId || !libraryName) return;
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: chatId,
          library: libraryName,
          question: userMessage.content,
          pdf_name: pdfName, // Include the PDF name in the request
          chat_mode: chatMode, // Include the chat mode
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString() + "-err",
            type: "error",
            content: err.detail || "Failed to get answer from backend.",
            timestamp: new Date().toISOString(),
          },
        ]);
      } else {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString() + "-a",
            type: "assistant",
            content: data.answer,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + "-err",
          type: "error",
          content: "Failed to get answer from backend.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-[calc(100vh-80px)] flex w-full">
      {/* Main Chat Area - Now takes full width */}
      <div className="flex-1 flex flex-col bg-black">
        {/* Chat Header */}
        <div className="bg-gray-900 border-b border-gray-800 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                to={`/library/${libraryName}`}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="h-6 w-6" />
              </Link>
              <div>
                <h2 className="text-xl font-bold text-white">{libraryName}</h2>
                <div className="flex items-center space-x-2">
                  {isLibraryMode ? (
                    <span className="text-sm text-blue-400 bg-blue-500/20 px-2 py-1 rounded">
                      📚 Library Mode - All PDFs
                    </span>
                  ) : (
                    <span className="text-sm text-red-400 bg-red-500/20 px-2 py-1 rounded">
                      📄 Single PDF: {pdfName}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {loading && messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-gray-400">Loading conversation...</p>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <MessageCircle className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-2xl font-semibold text-gray-400 mb-2">
                  Start a new conversation
                </h3>
                <p className="text-gray-500 mb-4">
                  Ask questions about {pdfName || libraryName} and get
                  AI-powered answers based on the content.
                </p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.type === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-3xl rounded-2xl p-4 ${
                    message.type === "user"
                      ? "bg-blue-600 text-white rounded-tr-none"
                      : message.type === "assistant"
                      ? "bg-gray-800 text-white rounded-tl-none"
                      : "bg-red-900/30 text-red-200 border border-red-500/30"
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    <div className="mt-1">
                      {message.type === "user" ? (
                        <div className="bg-blue-700 h-8 w-8 rounded-full flex items-center justify-center">
                          <User className="h-5 w-5 text-white" />
                        </div>
                      ) : message.type === "assistant" ? (
                        <div className="bg-gray-700 h-8 w-8 rounded-full flex items-center justify-center">
                          <Bot className="h-5 w-5 text-blue-400" />
                        </div>
                      ) : (
                        <div className="bg-red-900/50 h-8 w-8 rounded-full flex items-center justify-center">
                          <AlertCircle className="h-5 w-5 text-red-400" />
                        </div>
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="whitespace-pre-wrap">
                        {message.content}
                      </div>
                      <div className="mt-2 text-xs opacity-70">
                        {message.timestamp
                          ? new Date(message.timestamp).toLocaleTimeString()
                          : "No timestamp"}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-800 p-4">
          <div className="flex items-center space-x-2">
            <div className="flex-1 relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask a question..."
                className="w-full bg-gray-800 border border-gray-700 rounded-lg py-3 px-4 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={1}
                disabled={loading}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || loading}
              className="bg-blue-600 hover:bg-blue-500 text-white p-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;

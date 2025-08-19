import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  MessageSquare,
  Calendar,
  Filter,
  Search,
  X,
  FileText,
} from "lucide-react";

interface HistoryItem {
  id: string;
  libraryName: string;
  libraryId: string;
  pdfName: string;
  title: string;
  lastMessage: string;
  messageCount: number;
  timestamp: string;
  status: "active" | "archived";
}

const API_BASE = "http://localhost:8000";

const History = () => {
  const navigate = useNavigate();
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<HistoryItem[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<
    "all" | "active" | "archived"
  >("all");
  const [loading, setLoading] = useState(true);
  const [showPdfSelector, setShowPdfSelector] = useState(false);
  const [selectedLibrary, setSelectedLibrary] = useState<string | null>(null);
  const [pdfsInLibrary, setPdfsInLibrary] = useState<string[]>([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    filterHistory();
  }, [searchTerm, filterStatus, historyItems]);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE}/history`);
      if (!response.ok) throw new Error("Failed to fetch history");
      const data = await response.json();
      setHistoryItems(data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching history:", error);
      setLoading(false);
    }
  };

  const filterHistory = () => {
    let filtered = historyItems;

    if (searchTerm) {
      filtered = filtered.filter(
        (item) =>
          item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.libraryName.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.lastMessage.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filterStatus !== "all") {
      filtered = filtered.filter((item) => item.status === filterStatus);
    }

    setFilteredItems(filtered);
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return "Today";
    } else if (diffDays === 1) {
      return "Yesterday";
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const handleDelete = async (libraryId: string, pdfName?: string) => {
    if (
      !window.confirm(
        `Are you sure you want to delete this chat history${
          pdfName ? ` for "${pdfName}"` : ""
        }? This cannot be undone.`
      )
    )
      return;

    try {
      let url = `${API_BASE}/history/${encodeURIComponent(libraryId)}`;
      if (pdfName) {
        url += `?pdf_name=${encodeURIComponent(pdfName)}`;
      }

      const res = await fetch(url, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Failed to delete history");

      // If deleting a specific PDF's history, only remove that item
      if (pdfName) {
        setHistoryItems((prev) =>
          prev.filter(
            (item) =>
              !(item.libraryId === libraryId && item.pdfName === pdfName)
          )
        );
      } else {
        // Otherwise remove all items for this library
        setHistoryItems((prev) =>
          prev.filter((item) => item.libraryId !== libraryId)
        );
      }
    } catch (err) {
      alert("Failed to delete history");
    }
  };

  const handleContinueChat = (libraryId: string) => {
    // Find all PDFs in this library
    const pdfs = historyItems
      .filter((item) => item.libraryId === libraryId)
      .map((item) => item.pdfName);

    // Remove duplicates
    const uniquePdfs = Array.from(new Set(pdfs));

    if (uniquePdfs.length > 1) {
      // If multiple PDFs, show selector
      setSelectedLibrary(libraryId);
      setPdfsInLibrary(uniquePdfs);
      setShowPdfSelector(true);
    } else if (uniquePdfs.length === 1) {
      // If only one PDF, go directly to chat
      continueChatWithPdf(libraryId, uniquePdfs[0]);
    } else {
      // Fallback - should not happen
      continueChatWithPdf(libraryId, libraryId);
    }
  };

  const continueChatWithPdf = async (libraryId: string, pdfName: string) => {
    try {
      const res = await fetch(`${API_BASE}/chat/new`, { method: "POST" });
      if (!res.ok) throw new Error("Failed to create chat session");
      const data = await res.json();
      navigate(
        `/chat/${data.chat_id}?library=${encodeURIComponent(
          libraryId
        )}&pdf=${encodeURIComponent(pdfName)}&original_id=${encodeURIComponent(libraryId)}`
      );
    } catch (e) {
      alert("Failed to start new chat session");
    } finally {
      setShowPdfSelector(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-80px)] w-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading chat history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-4">Chat History</h1>
        <p className="text-gray-400">
          Review and continue your previous conversations
        </p>
      </div>

      {/* Search and Filter */}
      <div className="mb-8 flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
          />
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="text-gray-400 h-5 w-5" />
          <select
            value={filterStatus}
            onChange={(e) =>
              setFilterStatus(e.target.value as "all" | "active" | "archived")
            }
            className="bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            <option value="all">All Chats</option>
            <option value="active">Active</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      {/* History Timeline */}
      {filteredItems.length === 0 ? (
        <div className="text-center py-16">
          <MessageSquare className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-2xl font-semibold text-gray-400 mb-2">
            {searchTerm || filterStatus !== "all"
              ? "No matching conversations"
              : "No chat history yet"}
          </h3>
          <p className="text-gray-500 mb-6">
            {searchTerm || filterStatus !== "all"
              ? "Try adjusting your search or filter criteria"
              : "Start chatting with your documents to build up your history"}
          </p>
          {!searchTerm && filterStatus === "all" && (
            <Link
              to="/"
              className="inline-flex items-center space-x-2 bg-red-600 hover:bg-red-500 text-white px-6 py-3 rounded-lg transition-colors"
            >
              <span>Explore Libraries</span>
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className="group bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 hover:border-red-500/50 rounded-2xl p-6 transition-all duration-300 hover:shadow-xl hover:shadow-red-500/10"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-xl font-bold text-white group-hover:text-red-300 transition-colors">
                      {item.title}
                    </h3>
                    <span
                      className={`px-2 py-1 rounded-full text-xs ${
                        item.status === "active"
                          ? "bg-green-500/20 text-green-300"
                          : "bg-gray-500/20 text-gray-300"
                      }`}
                    >
                      {item.status}
                    </span>
                  </div>

                  <p className="text-gray-400 text-sm mb-3">
                    Library:{" "}
                    <span className="text-red-300">{item.libraryName}</span>
                  </p>

                  <p className="text-gray-300 mb-4 line-clamp-2">
                    {item.lastMessage}
                  </p>

                  <div className="flex items-center space-x-6 text-sm text-gray-400">
                    <span className="flex items-center space-x-1">
                      <MessageSquare className="h-4 w-4" />
                      <span>{item.messageCount} messages</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Calendar className="h-4 w-4" />
                      <span>{formatDate(item.timestamp)}</span>
                    </span>
                  </div>
                </div>

                <div className="flex flex-col items-end space-y-2 ml-6">
                  <button
                    onClick={() => handleContinueChat(item.libraryId)}
                    className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-colors text-sm"
                  >
                    Continue Chat
                  </button>
                  <button
                    onClick={() => handleDelete(item.libraryId, item.pdfName)}
                    className="bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-lg transition-colors text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* PDF Selector Modal */}
      {showPdfSelector && selectedLibrary && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-xl p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-white">
                Select a PDF to chat with
              </h3>
              <button
                onClick={() => setShowPdfSelector(false)}
                className="text-gray-400 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="max-h-96 overflow-y-auto space-y-2">
              {pdfsInLibrary.length > 0 ? (
                pdfsInLibrary.map((pdfName) => (
                  <div
                    key={pdfName}
                    onClick={() =>
                      continueChatWithPdf(selectedLibrary, pdfName)
                    }
                    className="flex items-center p-3 rounded-lg hover:bg-gray-700 cursor-pointer"
                  >
                    <div className="bg-red-500/20 p-2 rounded-lg mr-3">
                      <FileText className="h-5 w-5 text-red-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium">{pdfName}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-400 text-center py-4">
                  No PDFs available
                </p>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-700 flex justify-between">
              <button
                onClick={() => setShowPdfSelector(false)}
                className="px-4 py-2 text-gray-300 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={() =>
                  continueChatWithPdf(selectedLibrary, selectedLibrary)
                }
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg"
              >
                Chat with entire library
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default History;

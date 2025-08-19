import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ArrowLeft, MessageSquare, X } from "lucide-react";
import PDFUploadZone from "../components/PDFUploadZone";
import PDFList from "../components/PDFList";

const API_BASE = "http://localhost:8000";

interface PDF {
  id: string;
  name: string;
  size: number;
  tags: string[];
  uploadedAt: string;
  status: "ready" | "processing" | "error";
}

interface Library {
  name: string;
  description: string;
  documentCount: number;
  createdAt: string;
}

const LibraryView = () => {
  const { id } = useParams<{ id: string }>();
  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [libraryName, setLibraryName] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [showPdfSelector, setShowPdfSelector] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLibrary();
    // eslint-disable-next-line
  }, [id]);

  const fetchLibrary = async () => {
    setLoading(true);
    setError("");
    try {
      // Fetch all libraries and find the one matching the id
      const res = await fetch(`${API_BASE}/libraries`);
      if (!res.ok) throw new Error("Failed to fetch libraries");
      const libraries = (await res.json()) as Library[];
      const lib = libraries.find((l) => l.name === id);
      if (!lib) throw new Error("Library not found");
      setLibraryName(lib.name);
      // Fetch PDFs for this library
      const pdfRes = await fetch(
        `${API_BASE}/libraries/${encodeURIComponent(lib.name)}/pdfs`
      );
      const pdfList = pdfRes.ok ? ((await pdfRes.json()) as PDF[]) : [];
      setPdfs(pdfList);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load library";
      setError(errorMessage);
      setLibraryName("");
      setPdfs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (files: File[]) => {
    if (!libraryName) return;
    for (const file of files) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("library", libraryName);
      try {
        const res = await fetch(`${API_BASE}/upload`, {
          method: "POST",
          body: formData,
        });
        if (!res.ok) {
          const err = await res.json();
          alert(err.detail || "Failed to upload PDF");
        }
      } catch (e) {
        alert("Failed to upload PDF");
      }
    }
    // After upload, refresh library (PDF list)
    fetchLibrary();
  };

  const handleStartChat = async () => {
    // Show PDF selector modal instead of immediately starting chat
    setShowPdfSelector(true);
  };

  const startChatWithPdf = async (pdfName: string) => {
    try {
      const res = await fetch(`${API_BASE}/chat/new`, { method: "POST" });
      if (!res.ok) throw new Error("Failed to create chat session");
      const data = await res.json();
      navigate(
        `/chat/${data.chat_id}?library=${encodeURIComponent(
          libraryName
        )}&pdf=${encodeURIComponent(pdfName)}`
      );
    } catch (e) {
      alert("Failed to start new chat session");
    } finally {
      setShowPdfSelector(false);
    }
  };

  const startChatWithLibrary = async () => {
    try {
      const res = await fetch(`${API_BASE}/chat/new`, { method: "POST" });
      if (!res.ok) throw new Error("Failed to create chat session");
      const data = await res.json();
      navigate(
        `/chat/${data.chat_id}?library=${encodeURIComponent(
          libraryName
        )}&mode=library`
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
          <p className="text-gray-400">Loading library...</p>
        </div>
      </div>
    );
  }

  if (error || !libraryName) {
    return (
      <div className="w-full px-6 py-8 text-center">
        <h2 className="text-2xl font-bold text-gray-400 mb-4">
          {error || "Library not found"}
        </h2>
        <Link to="/" className="text-red-400 hover:text-red-300">
          ← Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-80px)] w-full">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-900/30 via-red-800/20 to-red-900/30 border-b border-red-500/20 w-full">
        <div className="w-full px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                to="/"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="h-6 w-6" />
              </Link>
              <h1 className="text-3xl font-bold text-white">{libraryName}</h1>
              <span className="px-3 py-1 bg-red-500/20 text-red-300 rounded-full text-sm">
                {pdfs.length} PDFs
              </span>
            </div>
            <button
              onClick={handleStartChat}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg transition-colors"
            >
              <MessageSquare className="h-5 w-5" />
              <span>Start Chat</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="w-full px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Zone */}
          <div className="lg:col-span-2">
            <PDFUploadZone onUpload={handleFileUpload} />
          </div>

          {/* PDF List */}
          <div className="lg:col-span-1">
            <PDFList pdfs={pdfs} />
          </div>
        </div>
      </div>

      {/* PDF Selector Modal */}
      {showPdfSelector && (
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

            <div className="space-y-2 max-h-80 overflow-y-auto">
              {/* Chat with Library Option */}
              <div className="flex items-center p-3 rounded-lg bg-blue-500/10 border border-blue-500/30 hover:bg-blue-500/20 cursor-pointer">
                <div className="bg-blue-500/20 p-2 rounded-lg mr-3">
                  <MessageSquare className="h-5 w-5 text-blue-400" />
                </div>
                <div className="flex-1">
                  <p className="text-blue-200 font-medium">Chat with Entire Library</p>
                  <p className="text-blue-300/70 text-sm">
                    Search across all {pdfs.length} PDF{pdfs.length !== 1 ? 's' : ''} at once
                  </p>
                </div>
                <button
                  onClick={startChatWithLibrary}
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg font-medium"
                >
                  Chat
                </button>
              </div>

              {/* Separator */}
              {pdfs.length > 0 && (
                <div className="flex items-center my-4">
                  <div className="flex-1 h-px bg-gray-600"></div>
                  <span className="px-3 text-gray-400 text-sm">Or chat with individual PDFs</span>
                  <div className="flex-1 h-px bg-gray-600"></div>
                </div>
              )}

              {/* Individual PDF Options */}
              {pdfs.length > 0 ? (
                pdfs.map((pdf) => (
                  <div
                    key={pdf.id}
                    className="flex items-center p-3 rounded-lg hover:bg-gray-700 cursor-pointer"
                  >
                    <div className="bg-red-500/20 p-2 rounded-lg mr-3">
                      <MessageSquare className="h-5 w-5 text-red-400" />
                    </div>
                    <div className="flex-1">
                      <p className="text-white font-medium">{pdf.name}</p>
                      <p className="text-gray-400 text-sm">
                        {(pdf.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <button
                      onClick={() => startChatWithPdf(pdf.name)}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg"
                    >
                      Chat
                    </button>
                  </div>
                ))
              ) : (
                <p className="text-gray-400 text-center py-4">
                  No PDFs available for individual chat
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LibraryView;

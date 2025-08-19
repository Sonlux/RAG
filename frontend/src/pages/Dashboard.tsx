import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Plus, FileText, ArrowRight } from "lucide-react";
import CreateLibraryModal from "../components/CreateLibraryModal";

interface Library {
  name: string;
  doc_count: number;
  created_at: string;
  description?: string;
}

const API_BASE = "http://localhost:8000";

const Dashboard = () => {
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLibraries();
  }, []);

  const fetchLibraries = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/libraries`);
      if (!res.ok) throw new Error("Failed to fetch libraries");
      const data = await res.json();
      setLibraries(data);
    } catch (error) {
      console.error("Error fetching libraries:", error);
      setLibraries([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLibrary = async (name: string) => {
    try {
      const res = await fetch(`${API_BASE}/libraries`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description: "" }),
      });
      if (!res.ok) {
        const err = await res.json();
        alert(err.detail || "Failed to create library");
        return;
      }
      await fetchLibraries();
    } catch (error) {
      alert("Failed to create library");
    }
  };

  const handleDeleteLibrary = async (name: string) => {
    if (!window.confirm(`Delete library "${name}" and all its data?`)) return;
    try {
      const res = await fetch(
        `${API_BASE}/libraries/${encodeURIComponent(name)}`,
        {
          method: "DELETE",
        }
      );
      if (!res.ok) {
        const err = await res.json();
        alert(err.detail || "Failed to delete library");
        return;
      }
      await fetchLibraries();
    } catch (error) {
      alert("Failed to delete library");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-80px)] w-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading your libraries...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full px-6 py-8">
      {/* Hero Section */}
      <div className="mb-12 text-center">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-red-500 via-red-400 to-red-300 bg-clip-text text-transparent animate-pulse">
          Your Knowledge Universe
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
          Organize your documents, ask intelligent questions, and discover
          insights through the power of AI
        </p>
      </div>

      {/* Create Library Button */}
      <div className="mb-8 flex justify-center">
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="group flex items-center space-x-3 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 px-8 py-4 rounded-xl font-semibold text-white transition-all duration-300 transform hover:scale-105 hover:shadow-2xl hover:shadow-red-500/25"
        >
          <Plus className="h-6 w-6 group-hover:rotate-90 transition-transform duration-300" />
          <span>Create New Library</span>
        </button>
      </div>

      {/* Libraries Grid */}
      {libraries.length === 0 ? (
        <div className="text-center py-16">
          <FileText className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-2xl font-semibold text-gray-400 mb-2">
            No libraries yet
          </h3>
          <p className="text-gray-500">
            Create your first library to get started
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {libraries.map((library) => (
            <Link
              key={library.name}
              to={`/library/${library.name}`}
              className="group relative bg-gradient-to-br from-gray-900 via-gray-800 to-black rounded-2xl p-6 border border-gray-700 hover:border-red-500/50 transition-all duration-300 transform hover:scale-105 hover:shadow-2xl hover:shadow-red-500/20"
            >
              {/* Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 to-blue-500/10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-red-300 transition-colors">
                      {library.name}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-400">
                      <span className="flex items-center space-x-1">
                        <FileText className="h-4 w-4" />
                        <span>{library.doc_count} PDFs</span>
                      </span>
                    </div>
                  </div>
                  <ArrowRight className="h-6 w-6 text-gray-400 group-hover:text-red-400 group-hover:translate-x-1 transition-all duration-300" />
                </div>

                <div className="text-xs text-gray-500 mb-4">
                  Created: {new Date(library.created_at).toLocaleDateString()}
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex space-x-2">
                    <Link
                      to={`/chat/${library.name}`}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg transition-colors"
                      onClick={(e) => e.stopPropagation()}
                    >
                      Chat
                    </Link>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleDeleteLibrary(library.name);
                      }}
                      className="ml-2 px-2 py-1 text-xs bg-red-700 hover:bg-red-600 text-white rounded"
                    >
                      Delete
                    </button>
                  </div>
                  <span className="text-xs text-gray-500">Enter Library →</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      <CreateLibraryModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreateLibrary={handleCreateLibrary}
      />
    </div>
  );
};

export default Dashboard;

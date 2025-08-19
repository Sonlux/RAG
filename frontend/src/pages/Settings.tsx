import React, { useState, useEffect } from "react";
import { User, Moon, Sun, Trash2, Save, Upload, LogOut } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

const Settings = () => {
  const { user, updateProfile, logout, loading } = useAuth();
  const navigate = useNavigate();
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [avatar, setAvatar] = useState<string>("");
  const [name, setName] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Load user data when component mounts
  useEffect(() => {
    if (user) {
      setName(user.name || "");
      setAvatar(user.avatar || "");
    }
  }, [user]);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!user && !loading) {
      navigate("/login");
    }
  }, [user, loading, navigate]);

  const handleAvatarUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setAvatar(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveSettings = async () => {
    try {
      await updateProfile(name, avatar);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (error) {
      console.error("Failed to update profile:", error);
    }
  };

  const handleClearHistory = () => {
    if (showDeleteConfirm) {
      // Simulate clearing history
      console.log("Clearing chat history");
      setShowDeleteConfirm(false);
    } else {
      setShowDeleteConfirm(true);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-80px)] w-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full px-6 py-8 max-w-full">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-4">Settings</h1>
        <p className="text-gray-400">Customize your PDFlix experience</p>
      </div>

      {saveSuccess && (
        <div className="bg-green-900/20 border border-green-500 text-green-500 px-4 py-3 rounded-lg mb-6">
          Settings saved successfully!
        </div>
      )}

      <div className="space-y-8">
        {/* Profile Section */}
        <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center space-x-2">
            <User className="h-6 w-6 text-red-400" />
            <span>Profile</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Avatar Upload */}
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-300">
                Profile Picture
              </label>
              <div className="flex items-center space-x-4">
                <div className="w-20 h-20 rounded-full bg-gray-700 flex items-center justify-center overflow-hidden">
                  {avatar ? (
                    <img
                      src={avatar}
                      alt="Avatar"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <User className="h-8 w-8 text-gray-400" />
                  )}
                </div>
                <label className="cursor-pointer bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2">
                  <Upload className="h-4 w-4" />
                  <span>Upload</span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Name and Email */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  placeholder="Enter your name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={user.email}
                  readOnly
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-gray-400"
                />
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={handleSaveSettings}
              className="flex items-center space-x-2 bg-green-600 hover:bg-green-500 px-6 py-3 rounded-lg text-white font-medium transition-colors"
            >
              <Save className="h-5 w-5" />
              <span>Save Changes</span>
            </button>
          </div>
        </div>

        {/* Appearance Section */}
        <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center space-x-2">
            <Sun className="h-6 w-6 text-yellow-400" />
            <span>Appearance</span>
          </h2>

          <div className="flex items-center space-x-4">
            <button
              onClick={() => setTheme("light")}
              className={`flex flex-col items-center space-y-2 p-4 rounded-xl transition-all ${
                theme === "light"
                  ? "bg-blue-500/20 border-2 border-blue-500"
                  : "bg-gray-800 border-2 border-transparent hover:border-gray-600"
              }`}
            >
              <Sun
                className={`h-8 w-8 ${
                  theme === "light" ? "text-blue-400" : "text-gray-400"
                }`}
              />
              <span
                className={
                  theme === "light" ? "text-blue-400" : "text-gray-400"
                }
              >
                Light
              </span>
            </button>

            <button
              onClick={() => setTheme("dark")}
              className={`flex flex-col items-center space-y-2 p-4 rounded-xl transition-all ${
                theme === "dark"
                  ? "bg-blue-500/20 border-2 border-blue-500"
                  : "bg-gray-800 border-2 border-transparent hover:border-gray-600"
              }`}
            >
              <Moon
                className={`h-8 w-8 ${
                  theme === "dark" ? "text-blue-400" : "text-gray-400"
                }`}
              />
              <span
                className={theme === "dark" ? "text-blue-400" : "text-gray-400"}
              >
                Dark
              </span>
            </button>
          </div>
        </div>

        {/* Data Management Section */}
        <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center space-x-2">
            <Trash2 className="h-6 w-6 text-red-400" />
            <span>Data Management</span>
          </h2>

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-medium text-white">
                  Clear Chat History
                </h3>
                <p className="text-gray-400 text-sm">
                  Delete all your conversation history
                </p>
              </div>
              {showDeleteConfirm ? (
                <div className="flex items-center space-x-2">
                  <span className="text-red-400">Are you sure?</span>
                  <button
                    onClick={handleClearHistory}
                    className="bg-red-600 hover:bg-red-500 px-4 py-2 rounded-lg text-white text-sm"
                  >
                    Yes, Delete
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg text-white text-sm"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button
                  onClick={handleClearHistory}
                  className="bg-gray-700 hover:bg-red-600 px-4 py-2 rounded-lg text-white text-sm transition-colors"
                >
                  Clear History
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Logout Button */}
        <div className="flex justify-center">
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 bg-gray-700 hover:bg-red-600 px-8 py-4 rounded-xl text-white font-medium transition-colors"
          >
            <LogOut className="h-5 w-5" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;

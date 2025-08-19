import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Library,
  MessageSquare,
  History,
  Settings,
  BookOpen,
  User,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext";

const Layout = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation();
  const { user } = useAuth();

  const navItems = [
    { path: "/", icon: Library, label: "Libraries" },
    { path: "/chat", icon: MessageSquare, label: "Chat" },
    { path: "/history", icon: History, label: "History" },
    { path: "/settings", icon: Settings, label: "Settings" },
  ];

  return (
    <div className="min-h-screen bg-black text-white w-full">
      {/* Header */}
      <header className="bg-gradient-to-r from-black via-red-900/20 to-black border-b border-red-500/20 w-full">
        <div className="w-full px-6 py-4">
          <div className="flex items-center justify-between">
            <Link
              to="/"
              className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
            >
              <BookOpen className="h-8 w-8 text-red-500" />
              <h1 className="text-2xl font-bold bg-gradient-to-r from-red-500 to-red-300 bg-clip-text text-transparent">
                PDFlix
              </h1>
            </Link>

            <div className="flex items-center space-x-6">
              <nav className="flex items-center space-x-6">
                {navItems.map(({ path, icon: Icon, label }) => (
                  <Link
                    key={path}
                    to={path}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                      location.pathname === path
                        ? "bg-red-500/20 text-red-400 shadow-lg shadow-red-500/25"
                        : "hover:bg-white/5 hover:text-red-300"
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span className="hidden md:block">{label}</span>
                  </Link>
                ))}
              </nav>

              {/* User Profile */}
              <Link
                to="/settings"
                className="flex items-center space-x-2 hover:bg-white/5 px-3 py-2 rounded-lg transition-all"
              >
                {user?.avatar ? (
                  <img
                    src={user.avatar}
                    alt={user.name}
                    className="h-8 w-8 rounded-full object-cover border border-red-500/30"
                  />
                ) : (
                  <div className="h-8 w-8 rounded-full bg-red-500/20 flex items-center justify-center">
                    <User className="h-4 w-4 text-red-400" />
                  </div>
                )}
                <span className="hidden md:block text-sm font-medium">
                  {user?.name || "User"}
                </span>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="min-h-[calc(100vh-80px)] w-full">{children}</main>
    </div>
  );
};

export default Layout;

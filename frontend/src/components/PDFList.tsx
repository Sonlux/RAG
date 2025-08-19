import React from "react";
import {
  FileText,
  Tag,
  Clock,
  AlertCircle,
  CheckCircle,
  Loader,
} from "lucide-react";

interface PDF {
  id: string;
  name: string;
  size: number;
  tags: string[];
  uploadedAt: string;
  status: "uploading" | "processing" | "ready" | "error";
}

interface PDFListProps {
  pdfs: PDF[];
}

const PDFList = ({ pdfs }: PDFListProps) => {
  const getStatusIcon = (status: PDF["status"]) => {
    switch (status) {
      case "uploading":
        return <Loader className="h-4 w-4 text-blue-500 animate-spin" />;
      case "processing":
        return <Loader className="h-4 w-4 text-yellow-500 animate-spin" />;
      case "ready":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusText = (status: PDF["status"]) => {
    switch (status) {
      case "uploading":
        return "Uploading...";
      case "processing":
        return "Processing...";
      case "ready":
        return "Ready";
      case "error":
        return "Error";
      default:
        return "";
    }
  };

  const getStatusColor = (status: PDF["status"]) => {
    switch (status) {
      case "uploading":
        return "text-blue-500";
      case "processing":
        return "text-yellow-500";
      case "ready":
        return "text-green-500";
      case "error":
        return "text-red-500";
      default:
        return "text-gray-500";
    }
  };

  if (pdfs.length === 0) {
    return (
      <div className="text-center py-12">
        <FileText className="h-16 w-16 text-gray-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-400 mb-2">
          No documents yet
        </h3>
        <p className="text-gray-500">Upload your first PDF to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {pdfs.map((pdf) => (
        <div
          key={pdf.id}
          className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-6 border border-gray-700 hover:border-red-500/30 transition-all duration-300"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4 flex-1">
              <div className="bg-red-500/20 p-3 rounded-lg">
                <FileText className="h-6 w-6 text-red-500" />
              </div>

              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-white mb-2 truncate">
                  {pdf.name}
                </h3>

                <div className="flex items-center space-x-4 text-sm text-gray-400 mb-3">
                  <span>{(pdf.size / 1024 / 1024).toFixed(2)} MB</span>
                  <span className="flex items-center space-x-1">
                    <Clock className="h-4 w-4" />
                    <span>{new Date(pdf.uploadedAt).toLocaleDateString()}</span>
                  </span>
                </div>

                {pdf.tags.length > 0 && (
                  <div className="flex items-center space-x-2 mb-3">
                    <Tag className="h-4 w-4 text-gray-400" />
                    <div className="flex flex-wrap gap-2">
                      {pdf.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-2">
              {getStatusIcon(pdf.status)}
              <span
                className={`text-sm font-medium ${getStatusColor(pdf.status)}`}
              >
                {getStatusText(pdf.status)}
              </span>
            </div>
          </div>

          {pdf.status === "processing" && (
            <div className="mt-4">
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-yellow-500 to-orange-500 h-2 rounded-full animate-pulse"
                  style={{ width: "60%" }}
                ></div>
              </div>
              <p className="text-xs text-gray-400 mt-1">
                Processing document for AI analysis...
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default PDFList;

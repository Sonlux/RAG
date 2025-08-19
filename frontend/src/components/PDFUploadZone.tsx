
import React, { useState, useCallback } from 'react';
import { Upload, FileText, X } from 'lucide-react';

interface PDFUploadZoneProps {
  onUpload: (files: File[]) => void;
}

const PDFUploadZone = ({ onUpload }: PDFUploadZoneProps) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = Array.from(e.dataTransfer.files).filter(
      file => file.type === 'application/pdf'
    );
    setSelectedFiles(files);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setSelectedFiles(files);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(files => files.filter((_, i) => i !== index));
  };

  const handleUpload = () => {
    if (selectedFiles.length > 0) {
      onUpload(selectedFiles);
      setSelectedFiles([]);
    }
  };

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
          isDragActive
            ? 'border-red-500 bg-red-500/10'
            : 'border-gray-600 hover:border-red-500/50 hover:bg-red-500/5'
        }`}
      >
        <Upload className={`h-12 w-12 mx-auto mb-4 ${isDragActive ? 'text-red-500' : 'text-gray-400'}`} />
        <p className="text-lg font-medium text-white mb-2">
          {isDragActive ? 'Drop your PDFs here' : 'Drag & drop PDFs here'}
        </p>
        <p className="text-gray-400 mb-4">or</p>
        <label className="inline-block bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 px-6 py-3 rounded-lg text-white font-medium cursor-pointer transition-all">
          Browse Files
          <input
            type="file"
            multiple
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
          />
        </label>
      </div>

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-medium text-white">Selected Files:</h3>
          {selectedFiles.map((file, index) => (
            <div key={index} className="flex items-center justify-between bg-gray-800 rounded-lg p-3">
              <div className="flex items-center space-x-3">
                <FileText className="h-5 w-5 text-red-500" />
                <div>
                  <p className="text-white font-medium">{file.name}</p>
                  <p className="text-gray-400 text-sm">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                onClick={() => removeFile(index)}
                className="text-gray-400 hover:text-red-400 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          ))}
          
          <button
            onClick={handleUpload}
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 px-6 py-3 rounded-lg text-white font-medium transition-all"
          >
            Upload {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''}
          </button>
        </div>
      )}
    </div>
  );
};

export default PDFUploadZone;

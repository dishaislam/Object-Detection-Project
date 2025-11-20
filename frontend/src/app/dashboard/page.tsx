'use client';

import { useState, useEffect, ChangeEvent } from 'react';
import { useRouter } from 'next/navigation';
import {
  detectObjects,
  askQuestion,
  isAuthenticated,
  removeToken,
  getCurrentUser,
} from '@/lib/api';
import type { Detection, DetectionResponse, AnswerResponse, User } from '@/types';
import DetectionTable from '@/components/DetectionTable';
import ChatBox from '@/components/chatbox';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<DetectionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/');
      return;
    }

    getCurrentUser()
      .then(setUser)
      .catch(() => {
        removeToken();
        router.push('/');
      });
  }, [router]);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file');
        return;
      }

      setSelectedFile(file);
      setError('');
      setDetectionResult(null);

      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const handleDetect = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await detectObjects(selectedFile);
      setDetectionResult(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Detection failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    removeToken();
    router.push('/');
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 bg-blue-600 rounded-full flex items-center justify-center">
              <svg
                className="h-6 w-6 text-white"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900">AI Object Detection</h1>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-gray-700">Welcome, {user.username}!</span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Upload Image</h2>

          <div className="flex flex-col space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select an image
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
              />
            </div>

            {previewUrl && (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-h-64 mx-auto rounded"
                />
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <button
              onClick={handleDetect}
              disabled={!selectedFile || loading}
              className="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Detecting Objects...' : 'Detect Objects'}
            </button>
          </div>
        </div>

        {/* Results Section */}
        {detectionResult && (
          <div className="space-y-8">
            {/* Annotated Image */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Detection Results</h2>
              <p className="text-sm text-gray-600 mb-4">
                Processing time: {detectionResult.processing_time.toFixed(3)}s |
                Objects detected: {detectionResult.detections.length}
              </p>
              <div className="border-2 border-gray-200 rounded-lg p-4">
                <img
                  src={detectionResult.annotated_image}
                  alt="Annotated"
                  className="max-w-full mx-auto rounded"
                />
              </div>
            </div>

            {/* Detection Table */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Detected Objects</h2>
              <DetectionTable detections={detectionResult.detections} />
            </div>

            {/* Q&A Section */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Ask Questions</h2>
              <p className="text-sm text-gray-600 mb-4">
                Ask questions about the detected objects
              </p>
              <ChatBox detections={detectionResult.detections} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
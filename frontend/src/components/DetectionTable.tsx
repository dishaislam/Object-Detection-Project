'use client';

import { useState, useMemo } from 'react';
import type { Detection } from '@/types';

interface Props {
  detections: Detection[];
}

type SortField = 'class_name' | 'confidence' | 'bbox_x1' | 'bbox_y1';
type SortOrder = 'asc' | 'desc';

export default function DetectionTable({ detections }: Props) {
  const [sortField, setSortField] = useState<SortField>('confidence');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const sortedDetections = useMemo(() => {
    const sorted = [...detections].sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortField) {
        case 'class_name':
          aValue = a.class_name;
          bValue = b.class_name;
          break;
        case 'confidence':
          aValue = a.confidence;
          bValue = b.confidence;
          break;
        case 'bbox_x1':
          aValue = a.bounding_box.x1;
          bValue = b.bounding_box.x1;
          break;
        case 'bbox_y1':
          aValue = a.bounding_box.y1;
          bValue = b.bounding_box.y1;
          break;
        default:
          return 0;
      }

      if (typeof aValue === 'string') {
        return sortOrder === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      } else {
        return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
      }
    });

    return sorted;
  }, [detections, sortField, sortOrder]);

  const SortIndicator = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return (
        <span className="text-gray-400">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M5 10l5-5 5 5H5z" />
          </svg>
        </span>
      );
    }

    return (
      <span className="text-blue-600">
        {sortOrder === 'asc' ? (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M5 10l5-5 5 5H5z" />
          </svg>
        ) : (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M15 10l-5 5-5-5h10z" />
          </svg>
        )}
      </span>
    );
  };

  if (detections.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No objects detected in the image.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              #
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              onClick={() => handleSort('class_name')}
            >
              <div className="flex items-center space-x-1">
                <span>Class Name</span>
                <SortIndicator field="class_name" />
              </div>
            </th>
            <th
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              onClick={() => handleSort('confidence')}
            >
              <div className="flex items-center space-x-1">
                <span>Confidence</span>
                <SortIndicator field="confidence" />
              </div>
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Bounding Box
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sortedDetections.map((detection, index) => (
            <tr key={index} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {index + 1}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {detection.class_name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <div className="flex items-center">
                  <div className="flex-1">
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className="bg-blue-600 h-2.5 rounded-full"
                        style={{ width: `${detection.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                  <span className="ml-2 text-gray-700">
                    {(detection.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                <div className="font-mono text-xs">
                  x1: {detection.bounding_box.x1.toFixed(1)}, 
                  y1: {detection.bounding_box.y1.toFixed(1)},<br />
                  x2: {detection.bounding_box.x2.toFixed(1)}, 
                  y2: {detection.bounding_box.y2.toFixed(1)}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
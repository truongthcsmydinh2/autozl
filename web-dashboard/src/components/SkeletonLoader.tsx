import React from 'react'

interface SkeletonLoaderProps {
  rows?: number
  className?: string
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ 
  rows = 3, 
  className = '' 
}) => {
  return (
    <div className={`animate-pulse ${className}`}>
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="border-b border-gray-200 last:border-b-0">
          <div className="px-6 py-4 flex items-center space-x-4">
            {/* Device ID skeleton */}
            <div className="h-4 bg-gray-300 rounded w-24"></div>
            
            {/* Name skeleton */}
            <div className="h-4 bg-gray-300 rounded w-32"></div>
            
            {/* IP Address skeleton */}
            <div className="h-4 bg-gray-300 rounded w-28"></div>
            
            {/* Phone skeleton */}
            <div className="h-4 bg-gray-300 rounded w-36"></div>
            
            {/* Status skeleton */}
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 bg-gray-300 rounded-full"></div>
              <div className="h-4 bg-gray-300 rounded w-16"></div>
            </div>
            
            {/* Actions skeleton */}
            <div className="flex space-x-2">
              <div className="h-8 bg-gray-300 rounded w-20"></div>
              <div className="h-8 bg-gray-300 rounded w-16"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export const TableSkeletonLoader: React.FC<{ rows?: number }> = ({ rows = 5 }) => {
  return (
    <div className="animate-pulse">
      <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
        <table className="min-w-full divide-y divide-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3">
                <div className="h-4 bg-gray-300 rounded w-20"></div>
              </th>
              <th className="px-6 py-3">
                <div className="h-4 bg-gray-300 rounded w-16"></div>
              </th>
              <th className="px-6 py-3">
                <div className="h-4 bg-gray-300 rounded w-24"></div>
              </th>
              <th className="px-6 py-3">
                <div className="h-4 bg-gray-300 rounded w-20"></div>
              </th>
              <th className="px-6 py-3">
                <div className="h-4 bg-gray-300 rounded w-16"></div>
              </th>
              <th className="px-6 py-3">
                <div className="h-4 bg-gray-300 rounded w-20"></div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {Array.from({ length: rows }).map((_, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="h-4 bg-gray-300 rounded w-24"></div>
                </td>
                <td className="px-6 py-4">
                  <div className="h-4 bg-gray-300 rounded w-32"></div>
                </td>
                <td className="px-6 py-4">
                  <div className="h-4 bg-gray-300 rounded w-28"></div>
                </td>
                <td className="px-6 py-4">
                  <div className="h-4 bg-gray-300 rounded w-36"></div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-2">
                    <div className="h-2 w-2 bg-gray-300 rounded-full"></div>
                    <div className="h-4 bg-gray-300 rounded w-16"></div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex space-x-2">
                    <div className="h-8 bg-gray-300 rounded w-20"></div>
                    <div className="h-8 bg-gray-300 rounded w-16"></div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default SkeletonLoader
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { getAuthHeader } = useAuth();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/stats`, {
        headers: getAuthHeader()
      });
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Total Tools</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stats?.total_tools || 0}</p>
            </div>
            <div className="text-4xl">🛠️</div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Active Tools</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stats?.active_tools || 0}</p>
            </div>
            <div className="text-4xl">✅</div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-yellow-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Featured Tools</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stats?.featured_tools || 0}</p>
            </div>
            <div className="text-4xl">⭐</div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Categories</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stats?.total_categories || 0}</p>
            </div>
            <div className="text-4xl">📁</div>
          </div>
        </div>
      </div>

      {/* Tools by Category */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Tools by Category</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {stats?.tools_by_category &&
            Object.entries(stats.tools_by_category).map(([category, count]) => (
              <div
                key={category}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <span className="font-medium text-gray-700">{category}</span>
                <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full font-semibold text-sm">
                  {count}
                </span>
              </div>
            ))}
        </div>
      </div>

      {/* Tools by Price Type */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Tools by Price Type</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {stats?.tools_by_price_type &&
            Object.entries(stats.tools_by_price_type).map(([priceType, count]) => (
              <div
                key={priceType}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <span className="font-medium text-gray-700">{priceType}</span>
                <span className="bg-pink-100 text-pink-700 px-3 py-1 rounded-full font-semibold text-sm">
                  {count}
                </span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

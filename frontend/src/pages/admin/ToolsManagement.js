import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

const ToolsManagement = () => {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const { getAuthHeader } = useAuth();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    try {
      const response = await axios.get(`${API}/tools`);
      setTools(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching tools:', error);
      setLoading(false);
    }
  };

  const toggleActive = async (toolId) => {
    try {
      await axios.patch(
        `${API}/admin/tools/${toolId}/toggle-active`,
        {},
        { headers: getAuthHeader() }
      );
      // Update local state
      setTools(tools.map(tool =>
        tool.id === toolId ? { ...tool, is_active: !tool.is_active } : tool
      ));
    } catch (error) {
      console.error('Error toggling active status:', error);
      alert('Failed to update tool status');
    }
  };

  const toggleFeatured = async (toolId) => {
    try {
      await axios.patch(
        `${API}/admin/tools/${toolId}/toggle-featured`,
        {},
        { headers: getAuthHeader() }
      );
      // Update local state
      setTools(tools.map(tool =>
        tool.id === toolId ? { ...tool, is_featured: !tool.is_featured } : tool
      ));
    } catch (error) {
      console.error('Error toggling featured status:', error);
      alert('Failed to update featured status');
    }
  };

  const deleteTool = async (toolId) => {
    if (!window.confirm('Are you sure you want to delete this tool?')) {
      return;
    }

    try {
      await axios.delete(`${API}/admin/tools/${toolId}`, {
        headers: getAuthHeader()
      });
      setTools(tools.filter(tool => tool.id !== toolId));
      alert('Tool deleted successfully');
    } catch (error) {
      console.error('Error deleting tool:', error);
      alert('Failed to delete tool');
    }
  };

  const filteredTools = tools.filter(tool =>
    tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tool.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <div className="bg-white rounded-xl shadow-md p-4">
        <input
          type="text"
          placeholder="Search tools by name or category..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
        />
      </div>

      {/* Tools Table */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gradient-to-r from-purple-600 to-pink-600 text-white">
              <tr>
                <th className="px-6 py-4 text-left font-semibold">Name</th>
                <th className="px-6 py-4 text-left font-semibold">Category</th>
                <th className="px-6 py-4 text-left font-semibold">Price</th>
                <th className="px-6 py-4 text-center font-semibold">Active</th>
                <th className="px-6 py-4 text-center font-semibold">Featured</th>
                <th className="px-6 py-4 text-center font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredTools.map((tool) => (
                <tr key={tool.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      {tool.image_url && (
                        <img
                          src={tool.image_url}
                          alt={tool.name}
                          className="w-10 h-10 rounded-lg object-cover"
                        />
                      )}
                      <div>
                        <p className="font-semibold text-gray-800">{tool.name}</p>
                        <p className="text-sm text-gray-500 line-clamp-1">{tool.description}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="bg-teal-100 text-teal-700 px-3 py-1 rounded-full text-sm font-medium">
                      {tool.category}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      tool.price_type === 'Free' ? 'bg-green-100 text-green-700' :
                      tool.price_type === 'Paid' ? 'bg-red-100 text-red-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {tool.price_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <button
                      onClick={() => toggleActive(tool.id)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        tool.is_active ? 'bg-green-500' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          tool.is_active ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <button
                      onClick={() => toggleFeatured(tool.id)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        tool.is_featured ? 'bg-yellow-500' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          tool.is_featured ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <button
                      onClick={() => deleteTool(tool.id)}
                      className="text-red-600 hover:text-red-800 font-medium transition-colors"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredTools.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No tools found
          </div>
        )}
      </div>
    </div>
  );
};

export default ToolsManagement;

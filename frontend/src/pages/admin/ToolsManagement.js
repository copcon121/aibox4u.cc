import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

const ToolsManagement = () => {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingTool, setEditingTool] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    price_type: 'Free',
    url: '',
    image_url: '',
    tags: '',
    is_active: true,
    is_featured: false
  });
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
      const response = await axios.patch(
        `${API}/admin/tools/${toolId}/toggle-active`,
        {},
        { headers: getAuthHeader() }
      );
      
      // Update local state with the new status from backend
      setTools(tools.map(tool =>
        tool.id === toolId ? { ...tool, is_active: response.data.is_active } : tool
      ));
      
    } catch (error) {
      console.error('Error toggling active status:', error);
      alert('Failed to update tool status: ' + (error.response?.data?.detail || error.message));
    }
  };

  const toggleFeatured = async (toolId) => {
    try {
      const response = await axios.patch(
        `${API}/admin/tools/${toolId}/toggle-featured`,
        {},
        { headers: getAuthHeader() }
      );
      
      // Update local state with the new status from backend
      setTools(tools.map(tool =>
        tool.id === toolId ? { ...tool, is_featured: response.data.is_featured } : tool
      ));
      
    } catch (error) {
      console.error('Error toggling featured status:', error);
      alert('Failed to update featured status: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteTool = async (toolId) => {
    if (!window.confirm('Are you sure you want to delete this tool? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(`${API}/admin/tools/${toolId}`, {
        headers: getAuthHeader()
      });
      
      // Remove tool from local state
      setTools(tools.filter(tool => tool.id !== toolId));
      alert('Tool deleted successfully!');
      
    } catch (error) {
      console.error('Error deleting tool:', error);
      alert('Failed to delete tool: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleAddNew = () => {
    setEditingTool(null);
    setFormData({
      name: '',
      description: '',
      category: '',
      price_type: 'Free',
      url: '',
      image_url: '',
      tags: '',
      is_active: true,
      is_featured: false
    });
    setShowModal(true);
  };

  const handleEdit = (tool) => {
    setEditingTool(tool);
    setFormData({
      name: tool.name || '',
      description: tool.description || '',
      category: tool.category || '',
      price_type: tool.price_type || 'Free',
      url: tool.url || '',
      image_url: tool.image_url || '',
      tags: Array.isArray(tool.tags) ? tool.tags.join(', ') : tool.tags || '',
      is_active: tool.is_active !== undefined ? tool.is_active : true,
      is_featured: tool.is_featured !== undefined ? tool.is_featured : false
    });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const submitData = {
        ...formData,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };

      if (editingTool) {
        // Update existing tool
        const response = await axios.put(
          `${API}/admin/tools/${editingTool.id}`,
          submitData,
          { headers: getAuthHeader() }
        );
        
        setTools(tools.map(tool => 
          tool.id === editingTool.id ? response.data : tool
        ));
        alert('Tool updated successfully!');
      } else {
        // Create new tool
        const response = await axios.post(
          `${API}/admin/tools`,
          submitData,
          { headers: getAuthHeader() }
        );
        
        setTools([response.data, ...tools]);
        alert('Tool created successfully!');
      }

      setShowModal(false);
      setEditingTool(null);
      
    } catch (error) {
      console.error('Error saving tool:', error);
      alert('Failed to save tool: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
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
      {/* Header with Add Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Tools Management</h2>
        <button
          onClick={handleAddNew}
          className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition flex items-center space-x-2"
        >
          <span>+</span>
          <span>Add New Tool</span>
        </button>
      </div>

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
                <th className="px-6 py-4 text-left font-semibold">Tool</th>
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
                          onError={(e) => e.target.style.display = 'none'}
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
                      title={tool.is_active ? 'Click to deactivate' : 'Click to activate'}
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
                      title={tool.is_featured ? 'Click to unfeature' : 'Click to feature'}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          tool.is_featured ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <div className="flex justify-center space-x-2">
                      <button
                        onClick={() => handleEdit(tool)}
                        className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition font-medium"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deleteTool(tool.id)}
                        className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition font-medium"
                      >
                        Delete
                      </button>
                    </div>
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

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                {editingTool ? 'Edit Tool' : 'Add New Tool'}
              </h3>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tool Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleChange('name', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description *
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => handleChange('description', e.target.value)}
                    rows="3"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category *
                    </label>
                    <input
                      type="text"
                      value={formData.category}
                      onChange={(e) => handleChange('category', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Price Type *
                    </label>
                    <select
                      value={formData.price_type}
                      onChange={(e) => handleChange('price_type', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                      required
                    >
                      <option value="Free">Free</option>
                      <option value="Paid">Paid</option>
                      <option value="Freemium">Freemium</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URL *
                  </label>
                  <input
                    type="url"
                    value={formData.url}
                    onChange={(e) => handleChange('url', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                    placeholder="https://example.com"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Image URL
                  </label>
                  <input
                    type="url"
                    value={formData.image_url}
                    onChange={(e) => handleChange('image_url', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                    placeholder="https://example.com/image.png"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => handleChange('tags', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                    placeholder="AI, chatbot, automation"
                  />
                </div>

                <div className="flex items-center space-x-6">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => handleChange('is_active', e.target.checked)}
                      className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Active</span>
                  </label>

                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.is_featured}
                      onChange={(e) => handleChange('is_featured', e.target.checked)}
                      className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Featured</span>
                  </label>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition"
                  >
                    {editingTool ? 'Update Tool' : 'Create Tool'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolsManagement;
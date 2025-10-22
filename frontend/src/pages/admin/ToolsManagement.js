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
    website_url: '',
    category: '',
    price_type: 'Free',
    image_url: '',
    tags: []
  });
  const [formErrors, setFormErrors] = useState({});
  const [submitLoading, setSubmitLoading] = useState(false);
  const { getAuthHeader } = useAuth();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    try {
      const response = await axios.get(`${API}/admin/tools`, {
        headers: getAuthHeader()
      });
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

  const handleEdit = (tool) => {
    setEditingTool(tool);
    setFormData({
      name: tool.name,
      description: tool.description,
      website_url: tool.website_url,
      category: tool.category,
      price_type: tool.price_type,
      image_url: tool.image_url || '',
      tags: tool.tags || []
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleAddNew = () => {
    setEditingTool(null);
    setFormData({
      name: '',
      description: '',
      website_url: '',
      category: '',
      price_type: 'Free',
      image_url: '',
      tags: []
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingTool(null);
    setFormData({
      name: '',
      description: '',
      website_url: '',
      category: '',
      price_type: 'Free',
      image_url: '',
      tags: []
    });
    setFormErrors({});
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleTagsChange = (e) => {
    const tagsString = e.target.value;
    const tagsArray = tagsString.split(',').map(tag => tag.trim()).filter(tag => tag !== '');
    setFormData(prev => ({
      ...prev,
      tags: tagsArray
    }));
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.name.trim()) {
      errors.name = 'Tool name is required';
    }
    
    if (!formData.description.trim()) {
      errors.description = 'Description is required';
    }
    
    if (!formData.website_url.trim()) {
      errors.website_url = 'URL is required';
    } else if (!/^https?:\/\/.+/.test(formData.website_url)) {
      errors.website_url = 'Please enter a valid URL (starting with http:// or https://)';
    }
    
    if (!formData.category.trim()) {
      errors.category = 'Category is required';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setSubmitLoading(true);
    try {
      if (editingTool) {
        // Update existing tool
        const response = await axios.put(
          `${API}/admin/tools/${editingTool.id}`,
          formData,
          { headers: getAuthHeader() }
        );
        
        // Update the tool in the list
        setTools(tools.map(tool => 
          tool.id === editingTool.id ? response.data : tool
        ));
        
        alert('Tool updated successfully');
      } else {
        // Create new tool
        const response = await axios.post(
          `${API}/admin/tools`,
          formData,
          { headers: getAuthHeader() }
        );
        
        // Add the new tool to the list
        setTools([response.data, ...tools]);
        
        alert('Tool created successfully');
      }
      
      handleCloseModal();
    } catch (error) {
      console.error('Error saving tool:', error);
      alert(`Failed to ${editingTool ? 'update' : 'create'} tool: ` + (error.response?.data?.detail || error.message));
    } finally {
      setSubmitLoading(false);
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
      {/* Header with Add Button */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Tools Management</h1>
        <button
          onClick={handleAddNew}
          className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 font-medium transition-colors flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
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
                    <div className="flex items-center justify-center space-x-3">
                      <button
                        onClick={() => handleEdit(tool)}
                        className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deleteTool(tool.id)}
                        className="text-red-600 hover:text-red-800 font-medium transition-colors"
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

      {/* Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-4 rounded-t-xl">
              <h2 className="text-2xl font-bold">{editingTool ? 'Edit Tool' : 'Add New Tool'}</h2>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {/* Tool Name */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Tool Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none ${
                    formErrors.name ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Enter tool name"
                />
                {formErrors.name && (
                  <p className="text-red-500 text-sm mt-1">{formErrors.name}</p>
                )}
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows="4"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none ${
                    formErrors.description ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Enter tool description"
                />
                {formErrors.description && (
                  <p className="text-red-500 text-sm mt-1">{formErrors.description}</p>
                )}
              </div>

              {/* URL */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Website URL <span className="text-red-500">*</span>
                </label>
                <input
                  type="url"
                  name="website_url"
                  value={formData.website_url}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none ${
                    formErrors.website_url ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="https://example.com"
                />
                {formErrors.website_url && (
                  <p className="text-red-500 text-sm mt-1">{formErrors.website_url}</p>
                )}
              </div>

              {/* Category and Price Type Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Category */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Category <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none ${
                      formErrors.category ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="e.g., Chatbot, Search, etc."
                  />
                  {formErrors.category && (
                    <p className="text-red-500 text-sm mt-1">{formErrors.category}</p>
                  )}
                </div>

                {/* Price Type */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Price Type <span className="text-red-500">*</span>
                  </label>
                  <select
                    name="price_type"
                    value={formData.price_type}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                  >
                    <option value="Free">Free</option>
                    <option value="Paid">Paid</option>
                    <option value="Freemium">Freemium</option>
                  </select>
                </div>
              </div>

              {/* Image URL */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Image URL (optional)
                </label>
                <input
                  type="url"
                  name="image_url"
                  value={formData.image_url}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                  placeholder="https://example.com/image.jpg"
                />
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Tags (comma separated, optional)
                </label>
                <input
                  type="text"
                  name="tags"
                  value={formData.tags.join(', ')}
                  onChange={handleTagsChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                  placeholder="AI, Chatbot, NLP"
                />
              </div>

              {/* Modal Footer */}
              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  disabled={submitLoading}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitLoading}
                  className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 font-medium transition-colors disabled:opacity-50"
                >
                  {submitLoading ? 'Saving...' : (editingTool ? 'Save Changes' : 'Create Tool')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolsManagement;

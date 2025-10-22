import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

const PagesManagement = () => {
  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPage, setEditingPage] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    content: '',
    is_published: true
  });
  const { getAuthHeader } = useAuth();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    fetchPages();
  }, []);

  const fetchPages = async () => {
    try {
      const response = await axios.get(`${API}/admin/pages`, {
        headers: getAuthHeader()
      });
      setPages(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching pages:', error);
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (editingPage) {
        // Update existing page
        await axios.put(
          `${API}/admin/pages/${editingPage.id}`,
          formData,
          { headers: getAuthHeader() }
        );
        alert('Page updated successfully');
      } else {
        // Create new page
        await axios.post(
          `${API}/admin/pages`,
          formData,
          { headers: getAuthHeader() }
        );
        alert('Page created successfully');
      }

      setShowModal(false);
      setEditingPage(null);
      setFormData({ title: '', slug: '', content: '', is_published: true });
      fetchPages();
    } catch (error) {
      console.error('Error saving page:', error);
      alert(error.response?.data?.detail || 'Failed to save page');
    }
  };

  const handleEdit = (page) => {
    setEditingPage(page);
    setFormData({
      title: page.title,
      slug: page.slug,
      content: page.content,
      is_published: page.is_published
    });
    setShowModal(true);
  };

  const handleDelete = async (pageId) => {
    if (!window.confirm('Are you sure you want to delete this page?')) {
      return;
    }

    try {
      await axios.delete(`${API}/admin/pages/${pageId}`, {
        headers: getAuthHeader()
      });
      alert('Page deleted successfully');
      fetchPages();
    } catch (error) {
      console.error('Error deleting page:', error);
      alert('Failed to delete page');
    }
  };

  const handleNewPage = () => {
    setEditingPage(null);
    setFormData({ title: '', slug: '', content: '', is_published: true });
    setShowModal(true);
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
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Pages Management</h2>
        <button
          onClick={handleNewPage}
          className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition"
        >
          + New Page
        </button>
      </div>

      {/* Pages List */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        {pages.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No pages found. Create your first page!
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {pages.map((page) => (
              <div key={page.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800">{page.title}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      Slug: <span className="font-mono bg-gray-100 px-2 py-1 rounded">{page.slug}</span>
                    </p>
                    <p className="text-gray-600 mt-2 line-clamp-2">{page.content}</p>
                    <div className="flex items-center space-x-4 mt-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        page.is_published
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {page.is_published ? 'Published' : 'Draft'}
                      </span>
                      <span className="text-xs text-gray-400">
                        Created: {new Date(page.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button
                      onClick={() => handleEdit(page)}
                      className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition font-medium"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(page.id)}
                      className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition font-medium"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-2xl font-bold text-gray-800">
                {editingPage ? 'Edit Page' : 'Create New Page'}
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Title
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Slug (URL path)
                </label>
                <input
                  type="text"
                  value={formData.slug}
                  onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none font-mono"
                  placeholder="about-us"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Content
                </label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                  rows="10"
                  required
                />
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_published"
                  checked={formData.is_published}
                  onChange={(e) => setFormData({ ...formData, is_published: e.target.checked })}
                  className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <label htmlFor="is_published" className="text-sm font-medium text-gray-700">
                  Published
                </label>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition"
                >
                  {editingPage ? 'Update Page' : 'Create Page'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PagesManagement;

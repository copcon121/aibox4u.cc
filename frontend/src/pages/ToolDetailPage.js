import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

function ToolDetail() {
  const { id } = useParams();
  const [tool, setTool] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTool();
  }, [id]);

  const fetchTool = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/tools/${id}`);
      setTool(response.data);
    } catch (error) {
      console.error('Error fetching tool:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-8">
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (!tool) {
    return (
      <div className="container mx-auto p-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Tool not found</h2>
          <Link to="/" className="text-blue-600 hover:underline">← Back to Home</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <div className="mb-6 text-sm text-gray-600">
          <Link to="/" className="hover:text-blue-600">Home</Link>
          <span className="mx-2">/</span>
          <Link to={`/?category=${tool.category}`} className="hover:text-blue-600">{tool.category}</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-800">{tool.name}</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-6">
              {/* Tool Image */}
              <div className="mb-6">
                <img 
                  src={tool.image_url || '/placeholder.png'} 
                  alt={tool.name}
                  className="w-full h-48 object-cover rounded-lg"
                  onError={(e) => {
                    e.target.src = '/placeholder.png';
                  }}
                />
              </div>

              {/* Badges */}
              <div className="flex flex-wrap gap-2 mb-6">
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  {tool.category}
                </span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  tool.price_type === 'Free' ? 'bg-green-100 text-green-800' :
                  tool.price_type === 'Paid' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {tool.price_type}
                </span>
              </div>

              {/* CTA Button */}
              <a
                href={tool.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white text-center py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-105 font-semibold mb-6"
              >
                Try {tool.name} →
              </a>

              {/* Tags */}
              {tool.tags && tool.tags.length > 0 && (
                <div className="border-t pt-4">
                  <h3 className="font-semibold mb-3 text-sm text-gray-600 uppercase tracking-wide">Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {tool.tags.map((tag, index) => (
                      <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs hover:bg-gray-200 cursor-pointer">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Meta Info */}
              <div className="border-t mt-4 pt-4 text-xs text-gray-500">
                <div className="flex justify-between mb-2">
                  <span>Added:</span>
                  <span className="font-medium">{new Date(tool.created_at).toLocaleDateString()}</span>
                </div>
                {tool.synced_from && (
                  <div className="flex justify-between">
                    <span>Source:</span>
                    <span className="font-medium">AI Tools Directory</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-8">
              {/* Title */}
              <h1 className="text-4xl font-bold mb-2 text-gray-900">{tool.name}</h1>
              
              <p className="text-gray-600 mb-8">
                {tool.description}
              </p>

              {/* Full Description with HTML (paragraphs, headings, lists) */}
              <div 
                className="prose prose-lg max-w-none
                  prose-headings:text-gray-900 prose-headings:font-bold
                  prose-h3:text-2xl prose-h3:mt-8 prose-h3:mb-4
                  prose-p:text-gray-700 prose-p:leading-relaxed prose-p:mb-4
                  prose-ul:list-disc prose-ul:ml-6 prose-ul:mb-6
                  prose-li:text-gray-700 prose-li:mb-2
                  prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline"
                dangerouslySetInnerHTML={{ __html: tool.description_full }}
              />

              {/* Bottom CTA */}
              <div className="mt-12 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
                <h3 className="text-xl font-bold mb-2 text-gray-900">Ready to try {tool.name}?</h3>
                <p className="text-gray-600 mb-4">Visit their website to get started</p>
                <a
                  href={tool.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-105 font-semibold"
                >
                  Visit {tool.name} Website →
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Related Tools Section (Optional - for future) */}
        {/* 
        <div className="mt-12">
          <h2 className="text-3xl font-bold mb-6">Similar Tools in {tool.category}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Related tools grid }
          </div>
        </div>
        */}
      </div>
    </div>
  );
}

export default ToolDetail;
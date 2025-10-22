import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '../App';
import './ToolDetailPage.css';

const ToolDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tool, setTool] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTool();
  }, [id]);

  const fetchTool = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/tools/${id}`);
      setTool(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching tool:', err);
      setError('Failed to load tool details.');
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error || !tool) {
    return (
      <div className="error-container">
        <p className="error">{error || 'Tool not found'}</p>
        <button className="btn-back" onClick={() => navigate('/')}>Back to Home</button>
      </div>
    );
  }

  return (
    <div className="tool-detail-page">
      <div className="detail-header">
        <button className="btn-back" onClick={() => navigate('/')}>← Back to Directory</button>
      </div>
      
      <div className="detail-container">
        <div className="detail-image-section">
          <img src={tool.image_url} alt={tool.name} className="detail-image" />
        </div>
        
        <div className="detail-content">
          <h1 className="detail-title">{tool.name}</h1>
          
          <div className="detail-badges">
            <span className="badge badge-category">{tool.category}</span>
            <span className="badge badge-price">{tool.price_type}</span>
            {tool.is_featured && <span className="badge badge-featured">Featured</span>}
          </div>
          
          <div className="detail-tags">
            {tool.tags.map((tag, index) => (
              <span key={index} className="tag">{tag}</span>
            ))}
          </div>
          
          <p className="detail-description">{tool.description}</p>
          
          <a 
            href={tool.website_url} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="btn-visit"
          >
            Visit Website →
          </a>
          
          <div className="detail-meta">
            <p><strong>Category:</strong> {tool.category}</p>
            <p><strong>Pricing:</strong> {tool.price_type}</p>
            <p><strong>Added:</strong> {new Date(tool.created_at).toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ToolDetailPage;
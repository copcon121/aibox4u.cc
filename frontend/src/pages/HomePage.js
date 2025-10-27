import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { API } from '../App';

const HomePage = () => {
  const [tools, setTools] = useState([]);
  const [featuredTools, setFeaturedTools] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [isFetchingMore, setIsFetchingMore] = useState(false);

  // Site settings state - THÊM MỚI
  const [siteSettings, setSiteSettings] = useState({
    site_name: 'AI BOX FOR YOU',
    site_logo_url: '',
    site_description: "Explore the ultimate AI toolbox — trusted, verified, and beautifully organized"
  });

  useEffect(() => {
    document.title = 'AI BOX FOR YOU';
  }, []);
  
  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedPriceType, setSelectedPriceType] = useState('All');
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchInitialData();
    fetchSiteSettings(); // THÊM MỚI
  }, []);

  const hasInitializedFilters = useRef(false);

  useEffect(() => {
    if (!hasInitializedFilters.current) {
      return;
    }
    fetchToolsWithFilters(1, true);
  }, [searchQuery, selectedCategory, selectedPriceType]);

  // THÊM FUNCTION MỚI
  const fetchSiteSettings = async () => {
    try {
      const response = await axios.get(`${API}/admin/site-settings`);
      setSiteSettings(response.data);
    } catch (err) {
      console.error('Error fetching site settings:', err);
      // Giữ giá trị mặc định nếu API lỗi
    }
  };

  const PAGE_SIZE = 24;

  const normalizeToolsResponse = (data) => {
    if (Array.isArray(data)) {
      return {
        items: data,
        total: null,
        pageSize: data.length || PAGE_SIZE
      };
    }

    return {
      items: data.items || [],
      total: typeof data.total === 'number' ? data.total : null,
      pageSize: data.page_size || PAGE_SIZE
    };
  };

  const buildToolParams = (pageToLoad) => ({
    search: searchQuery || undefined,
    category: selectedCategory !== 'All' ? selectedCategory : undefined,
    price_type: selectedPriceType !== 'All' ? selectedPriceType : undefined,
    page: pageToLoad,
    page_size: PAGE_SIZE
  });

  const determineHasMore = (pageToLoad, pageSize, total, receivedCount) => {
    if (typeof total === 'number' && total >= 0) {
      return pageToLoad * pageSize < total;
    }
    return receivedCount === pageSize;
  };

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const params = buildToolParams(1);
      const [toolsRes, featuredRes, categoriesRes] = await Promise.all([
        axios.get(`${API}/tools`, { params }),
        axios.get(`${API}/tools/featured`),
        axios.get(`${API}/categories`)
      ]);

      const { items, total, pageSize } = normalizeToolsResponse(toolsRes.data);
      setTools(items);
      setFeaturedTools(featuredRes.data);
      setCategories(['All', ...categoriesRes.data]);
      setPage(1);
      setHasMore(determineHasMore(1, pageSize, total, items.length));
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load tools. Please try again later.');
    } finally {
      hasInitializedFilters.current = true;
      setLoading(false);
    }
  };

  const fetchToolsWithFilters = async (pageToLoad = 1, replace = true) => {
    if (pageToLoad === 1) {
      setLoading(true);
    } else {
      setIsFetchingMore(true);
    }

    try {
      const params = buildToolParams(pageToLoad);
      const response = await axios.get(`${API}/tools`, { params });
      const { items, total, pageSize } = normalizeToolsResponse(response.data);

      setTools((prev) => (replace || pageToLoad === 1 ? items : [...prev, ...items]));
      setPage(pageToLoad);
      setHasMore(determineHasMore(pageToLoad, pageSize, total, items.length));
      setError(null);
    } catch (err) {
      console.error('Error fetching tools:', err);
      if (pageToLoad === 1) {
        setError('Failed to load tools. Please try again later.');
      }
    } finally {
      if (pageToLoad === 1) {
        setLoading(false);
      } else {
        setIsFetchingMore(false);
      }
    }
  };

  const handleLoadMore = () => {
    if (!hasMore || isFetchingMore) {
      return;
    }
    fetchToolsWithFilters(page + 1, false);
  };

  const handleToolClick = (toolId) => {
    navigate(`/tool/${toolId}`);
  };

  if (loading) {
    return <div className="loading">Loading {siteSettings.site_name}...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div>
      {/* Hero Section */}
      <div className="hero-section">
        <div className="logo-section">
          <a href="/" className="logo">
            {/* THAY ĐỔI: Hiển thị logo động */}
            {siteSettings.site_logo_url ? (
              <img
                src={siteSettings.site_logo_url}
                alt={siteSettings.site_name} 
                style={{ height: '50px', maxWidth: '200px', objectFit: 'contain' }}
              />
            ) : (
              <>
                <div className="logo-icon">AI</div>
                <span>AI BOX<br />FOR YOU</span>
              </>
            )}
          </a>
        </div>
        <div className="hero-content">
          {/* THAY ĐỔI: Dùng siteSettings thay vì hard-coded */}
          <h1 className="hero-title">{siteSettings.site_name}</h1>
          <p className="hero-subtitle">{siteSettings.site_description}</p>
        </div>
      </div>

      {/* Search and Filter Section */}
      <div className="search-section">
        <div className="search-container">
          <input
            type="text"
            className="search-input"
            placeholder="Search AI tool or category"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <div className="filters">
            <select
              className="filter-select"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="All">All Categories</option>
              {categories.filter(cat => cat !== 'All').map((category) => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
            <select
              className="filter-select"
              value={selectedPriceType}
              onChange={(e) => setSelectedPriceType(e.target.value)}
            >
              <option value="All">All Prices</option>
              <option value="Free">Free</option>
              <option value="Freemium">Freemium</option>
              <option value="Paid">Paid</option>
            </select>
          </div>
        </div>
      </div>

      {/* Featured Tools Section */}
      {featuredTools.length > 0 && (
        <div className="featured-section">
          <h2 className="section-title">Featured Tools</h2>
          <div className="featured-grid">
            {featuredTools.map((tool) => (
              <div key={tool.id} className="featured-card">
                <div className="featured-badge">Featured Tool: {tool.name}</div>
                <div
                  className="featured-image-wrapper"
                  role="button"
                  tabIndex={0}
                  onClick={() => handleToolClick(tool.id)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault();
                      handleToolClick(tool.id);
                    }
                  }}
                >
                  <img src={tool.image_url} alt={tool.name} className="featured-image" />
                </div>
                <div className="featured-content">
                  <h3 className="featured-title">{tool.name}</h3>
                  <p className="featured-description">{tool.description}</p>
                  <a href={tool.website_url} target="_blank" rel="noopener noreferrer" className="featured-link">
                    Claim FREE 1 month Pro →
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Tools Section */}
      <div className="tools-section">
        <h2 className="section-title">All AI Tools</h2>
        {tools.length === 0 ? (
          <div className="no-results">No tools found matching your criteria.</div>
        ) : (
          <div className="tools-grid">
            {tools.map((tool) => (
              <div key={tool.id} className="tool-card">
                <div
                  className="tool-image-wrapper"
                  role="button"
                  tabIndex={0}
                  onClick={() => handleToolClick(tool.id)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault();
                      handleToolClick(tool.id);
                    }
                  }}
                >
                  <img src={tool.image_url} alt={tool.name} className="tool-image" />
                </div>
                <div className="tool-content">
                  <div className="tool-header">
                    <h3 className="tool-name">{tool.name}</h3>
                    <div className="tool-badges">
                      <span className="badge badge-category">{tool.category}</span>
                      {tool.tags.slice(0, 2).map((tag, index) => (
                        <span key={index} className="badge badge-tag">{tag}</span>
                      ))}
                    </div>
                  </div>
                  <p className="tool-description">{tool.description}</p>
                  <div className="tool-footer">
                    <span className="price-badge">{tool.price_type}</span>
                    <button className="btn-details" onClick={() => handleToolClick(tool.id)}>
                      Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      {tools.length > 0 && (
        <div className="load-more-container">
          <button
            className="load-more-button"
            onClick={handleLoadMore}
            disabled={!hasMore || isFetchingMore}
          >
            {isFetchingMore ? 'Loading more...' : hasMore ? 'Load more tools' : 'All tools loaded'}
          </button>
        </div>
      )}
    </div>
  );
};

export default HomePage;

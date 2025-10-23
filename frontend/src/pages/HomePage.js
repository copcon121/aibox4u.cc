import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { API } from '../App';

const PAGE_SIZE = 24;

const isAbortError = (error) =>
  error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED';

const HomePage = () => {
  const [tools, setTools] = useState([]);
  const [featuredTools, setFeaturedTools] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  // Site settings state - THÊM MỚI
  const [siteSettings, setSiteSettings] = useState({
    site_name: 'AI BOX FOR YOU',
    site_logo_url: '',
    site_description:
      'Explore the ultimate AI toolbox — trusted, verified, and beautifully organized',
  });

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedPriceType, setSelectedPriceType] = useState('All');

  const navigate = useNavigate();
  const abortRef = useRef(null);
  const filtersInitializedRef = useRef(false);
  const toolsCountRef = useRef(0);

  useEffect(() => {
    toolsCountRef.current = tools.length;
  }, [tools.length]);

  const fetchSiteSettings = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/admin/site-settings`);
      setSiteSettings(response.data);
    } catch (err) {
      console.error('Error fetching site settings:', err);
      // Giữ giá trị mặc định nếu API lỗi
    }
  }, [API]);

  const fetchInitialData = useCallback(async () => {
    setError(null);
    setLoading(true);

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const [toolsRes, featuredRes, categoriesRes] = await Promise.all([
        axios.get(`${API}/tools`, {
          params: { page: 1, limit: PAGE_SIZE },
          signal: controller.signal,
        }),
        axios.get(`${API}/tools/featured`),
        axios.get(`${API}/categories`),
      ]);

      const totalHeader = Number(toolsRes.headers['x-total-count']);
      const safeTotal = Number.isFinite(totalHeader)
        ? totalHeader
        : toolsRes.data.length;

      const uniqueCategories = Array.from(
        new Set(['All', ...categoriesRes.data.filter(Boolean)])
      );

      setTools(toolsRes.data);
      setFeaturedTools(featuredRes.data);
      setCategories(uniqueCategories);
      setTotalCount(safeTotal);
      setPage(1);
      setHasLoaded(true);
    } catch (err) {
      if (isAbortError(err)) {
        return;
      }

      console.error('Error fetching data:', err);
      setError('Failed to load tools. Please try again later.');
    } finally {
      if (abortRef.current === controller) {
        abortRef.current = null;
      }
      setLoading(false);
    }
  }, [API]);

  const fetchTools = useCallback(
    async ({ page: nextPage = 1, append = false } = {}) => {
      const isLoadMore = append && nextPage > 1;
      const shouldShowFullLoading =
        !isLoadMore && (!hasLoaded || toolsCountRef.current === 0);

      if (shouldShowFullLoading) {
        setLoading(true);
      } else if (!isLoadMore) {
        setLoading(false);
      }

      if (!isLoadMore) {
        setError(null);
      } else {
        setIsLoadingMore(true);
      }

      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      const params = {
        search: searchQuery || undefined,
        category: selectedCategory !== 'All' ? selectedCategory : undefined,
        price_type:
          selectedPriceType !== 'All' ? selectedPriceType : undefined,
        page: nextPage,
        limit: PAGE_SIZE,
      };

      try {
        const response = await axios.get(`${API}/tools`, {
          params,
          signal: controller.signal,
        });

        const incomingTools = response.data;
        const headerTotal = Number(response.headers['x-total-count']);

        setTotalCount((prevTotal) => {
          if (Number.isFinite(headerTotal)) {
            return headerTotal;
          }

          if (isLoadMore) {
            return Math.max(
              prevTotal,
              (nextPage - 1) * PAGE_SIZE + incomingTools.length
            );
          }

          return incomingTools.length;
        });

        setPage(nextPage);
        setTools((prevTools) => {
          if (!isLoadMore) {
            return incomingTools;
          }

          const existingIds = new Set(prevTools.map((tool) => tool.id));
          const merged = incomingTools.filter(
            (tool) => !existingIds.has(tool.id)
          );

          return [...prevTools, ...merged];
        });

        if (!hasLoaded) {
          setHasLoaded(true);
        }
      } catch (err) {
        if (isAbortError(err)) {
          return;
        }

        console.error('Error fetching tools:', err);
        if (!isLoadMore) {
          setError('Failed to load tools. Please try again later.');
          setTools([]);
        }
      } finally {
        if (abortRef.current === controller) {
          abortRef.current = null;
        }

        if (isLoadMore) {
          setIsLoadingMore(false);
        }
        if (!isLoadMore || shouldShowFullLoading) {
          setLoading(false);
        }
      }
    },
    [API, hasLoaded, searchQuery, selectedCategory, selectedPriceType]
  );

  useEffect(() => {
    fetchInitialData();
    fetchSiteSettings();

    return () => {
      abortRef.current?.abort();
    };
  }, [fetchInitialData, fetchSiteSettings]);

  useEffect(() => {
    if (!hasLoaded) {
      return;
    }

    if (!filtersInitializedRef.current) {
      filtersInitializedRef.current = true;
      return;
    }

    const debounceTimer = setTimeout(() => {
      setPage(1);
      setTotalCount(0);
      fetchTools({ page: 1, append: false });
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [searchQuery, selectedCategory, selectedPriceType, hasLoaded, fetchTools]);

  useEffect(() => () => abortRef.current?.abort(), []);

  const handleToolClick = (toolId) => {
    navigate(`/tool/${toolId}`);
  };

  const handleLoadMore = useCallback(() => {
    if (isLoadingMore || loading) {
      return;
    }

    fetchTools({ page: page + 1, append: true });
  }, [fetchTools, isLoadingMore, loading, page]);

  const hasMore = tools.length < totalCount;

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
                <span>AI TOOLS
                  <br />
                  DIRECTORY
                </span>
              </>
            )}
          </a>
          <div className="header-buttons">
            <button className="btn-header btn-submit">Submit Tool</button>
            <button className="btn-header btn-advertise">Advertise</button>
          </div>
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
              {categories
                .filter((cat) => cat !== 'All')
                .map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
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
                <img src={tool.image_url} alt={tool.name} className="featured-image" />
                <div className="featured-content">
                  <h3 className="featured-title">{tool.name}</h3>
                  <p className="featured-description">{tool.description}</p>
                  <a
                    href={tool.website_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="featured-link"
                  >
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
                <img src={tool.image_url} alt={tool.name} className="tool-image" />
                <div className="tool-content">
                  <div className="tool-header">
                    <h3 className="tool-name">{tool.name}</h3>
                    <div className="tool-badges">
                      <span className="badge badge-category">{tool.category}</span>
                      {tool.tags.slice(0, 2).map((tag, index) => (
                        <span key={index} className="badge badge-tag">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <p className="tool-description">{tool.description}</p>
                  <div className="tool-footer">
                    <span className="price-badge">{tool.price_type}</span>
                    <button
                      className="btn-details"
                      onClick={() => handleToolClick(tool.id)}
                    >
                      Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && hasMore && (
          <div className="load-more-container">
            <button
              className="btn-load-more"
              onClick={handleLoadMore}
              disabled={isLoadingMore}
            >
              {isLoadingMore ? 'Loading...' : 'Load more tools'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;

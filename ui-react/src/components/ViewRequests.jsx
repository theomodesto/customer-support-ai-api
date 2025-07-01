import { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { getSupportRequests } from '../utils/api'
import { showError } from '../utils/notifications'

const ViewRequests = ({ showLoading, hideLoading }) => {
  const [requests, setRequests] = useState([])
  const [pagination, setPagination] = useState({
    page: 1,
    size: 20,
    total: 0,
    has_next: false
  })
  const [filters, setFilters] = useState({
    category: '',
    priority: ''
  })

  const loadRequests = async (currentPage = pagination.page, currentFilters = filters) => {
    showLoading('Loading requests...')
    
    try {
      const data = await getSupportRequests(currentPage, pagination.size, currentFilters)
      setRequests(data.support_tickets)
      setPagination(prev => ({
        ...prev,
        page: data.page,
        total: data.total,
        has_next: data.has_next
      }))
    } catch (error) {
      showError(`Failed to load requests: ${error.message}`)
    } finally {
      hideLoading()
    }
  }

  useEffect(() => {
    loadRequests(pagination.page, filters)
  }, [pagination.page, pagination.size])

  useEffect(() => {
    // Reset to page 1 when filters change and reload
    setPagination(prev => ({ ...prev, page: 1 }))
    loadRequests(1, filters)
  }, [filters])

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilters(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const goToPage = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }))
  }

  const renderRequest = (ticket) => {
    const { id, priority, subject, body, created_at, language, category, confidence_score, summary } = ticket
    
    return (
      <div key={id} className="request-item">
        <div className="request-header">
          <span className="request-id">ID: {id}</span>
          <div>
            {priority && (
              <span 
                className={`request-priority ${priority}`}
                style={{
                  backgroundColor: 
                    priority === 'low' ? '#28a745' :
                    priority === 'medium' ? '#ffc107' :
                    priority === 'high' ? '#dc3545' : '#6c757d',
                  color: priority === 'medium' ? '#000' : '#fff',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  fontSize: '0.8em',
                  fontWeight: 'bold'
                }}
              >
                {priority}
              </span>
            )}
            <span className={`request-category ${category?.toLowerCase() || 'general'}`}>
              {category || 'Unknown'}
            </span>
          </div>
        </div>
        <div className="request-content">
          {subject && <div className="request-subject"><strong>{subject}</strong></div>}
          {body && <div className="request-body">{body}</div>}
          <div className="request-meta">
            <span>Created: {new Date(created_at).toLocaleString()}</span>
            <span>Language: {language || 'en'}</span>
          </div>
        </div>
        {category && (
          <div className="ai-result">
            <h4><i className="fas fa-brain"></i> AI Classification</h4>
            <p><strong>Category:</strong> {category}</p>
            <p><strong>Confidence:</strong> {(confidence_score * 100).toFixed(1)}%</p>
            <div className="confidence_score-bar">
              <div 
                className="confidence_score-fill" 
                style={{ width: `${confidence_score * 100}%` }}
              ></div>
            </div>
            {summary && <p><strong>Summary:</strong> {summary}</p>}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="card">
      <h2><i className="fas fa-list"></i> Support Requests</h2>
      
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="categoryFilter">Category:</label>
          <select
            id="categoryFilter"
            name="category"
            className="form-control"
            value={filters.category}
            onChange={handleFilterChange}
          >
            <option value="">All Categories</option>
            <option value="technical">Technical</option>
            <option value="billing">Billing</option>
            <option value="general">General</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label htmlFor="priorityFilter">Priority:</label>
          <select
            id="priorityFilter"
            name="priority"
            className="form-control"
            value={filters.priority}
            onChange={handleFilterChange}
          >
            <option value="">All Priorities</option>
            <option value="low" style={{ color: '#28a745' }}>🟢 Low</option>
            <option value="medium" style={{ color: '#ffc107' }}>🟡 Medium</option>
            <option value="high" style={{ color: '#dc3545' }}>🔴 High</option>
          </select>
        </div>
      </div>

      <div className="pagination-controls">
        <button 
          className="btn btn-outline" 
          disabled={pagination.page <= 1}
          onClick={() => goToPage(pagination.page - 1)}
        >
          <i className="fas fa-chevron-left"></i> Previous
        </button>
        <span>Page {pagination.page} of {Math.ceil(pagination.total / pagination.size)} ({pagination.total} total)</span>
        <button 
          className="btn btn-outline"
          disabled={!pagination.has_next}
          onClick={() => goToPage(pagination.page + 1)}
        >
          Next <i className="fas fa-chevron-right"></i>
        </button>
      </div>

      <div className="requests-list">
        {requests.length === 0 ? (
          <p className="no-data">No requests found</p>
        ) : (
          requests.map(renderRequest)
        )}
      </div>
    </div>
  )
}

ViewRequests.propTypes = {
  showLoading: PropTypes.func.isRequired,
  hideLoading: PropTypes.func.isRequired
}

export default ViewRequests 
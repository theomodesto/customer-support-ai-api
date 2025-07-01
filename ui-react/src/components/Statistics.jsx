import { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { getStatistics } from '../utils/api'
import { showError } from '../utils/notifications'

const Statistics = ({ showLoading, hideLoading }) => {
  const [stats, setStats] = useState(null)

  const loadStats = async () => {
    showLoading('Loading statistics...')
    
    try {
      const data = await getStatistics()
      setStats(data)
    } catch (error) {
      showError(`Failed to load statistics: ${error.message}`)
    } finally {
      hideLoading()
    }
  }

  useEffect(() => {
    loadStats()
  }, [])

  if (!stats) {
    return (
      <div className="card">
        <h2><i className="fas fa-chart-bar"></i> Statistics</h2>
        <p>Loading statistics...</p>
      </div>
    )
  }

  return (
    <div className="card">
      <h2><i className="fas fa-chart-bar"></i> Statistics</h2>
      <p className="stats-timeframe">Last 7 days</p>
      
      <div className="stats-controls">
        <button onClick={loadStats} className="btn btn-secondary">
          <i className="fas fa-sync-alt"></i> Refresh
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{stats.total_support_tickets}</div>
          <div className="stat-label">Total Requests</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.category_counts?.technical || 0}</div>
          <div className="stat-label">Technical</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.category_counts?.billing || 0}</div>
          <div className="stat-label">Billing</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.category_counts?.general || 0}</div>
          <div className="stat-label">General</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.priority_counts?.low || 0}</div>
          <div className="stat-label">Low Priority</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.priority_counts?.medium || 0}</div>
          <div className="stat-label">Medium Priority</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.priority_counts?.high || 0}</div>
          <div className="stat-label">High Priority</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{(stats.avg_confidence * 100).toFixed(1)}%</div>
          <div className="stat-label">Avg Confidence</div>
        </div>
      </div>
    </div>
  )
}

Statistics.propTypes = {
  showLoading: PropTypes.func.isRequired,
  hideLoading: PropTypes.func.isRequired
}

export default Statistics 
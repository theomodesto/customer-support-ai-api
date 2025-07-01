import { useState } from 'react'
import PropTypes from 'prop-types'
import { createSupportRequest } from '../utils/api'
import { showError } from '../utils/notifications'

const CreateRequest = ({ showLoading, hideLoading }) => {
  const [formData, setFormData] = useState({
    subject: '',
    body: '',
    language: 'en',
    priority: 'medium'
  })
  const [result, setResult] = useState(null)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const { language, subject, body, priority } = formData
    
    if (!subject.trim() || !body.trim()) {
      showError('Please enter both subject and body')
      return
    }
    
    const requestData = {
      language,
      priority,
      subject: subject.trim(),
      body: body.trim()
    }
    
    showLoading('Creating support request...')
    
    try {
      const result = await createSupportRequest(requestData)
      setResult(result)
      
      // Reset form
      setFormData({
        subject: '',
        body: '',
        language: 'en',
        priority: 'medium'
      })
    } catch (error) {
      showError(`Failed to create request: ${error.message}`)
    } finally {
      hideLoading()
    }
  }

  return (
    <>
      <div className="card">
        <h2><i className="fas fa-plus-circle"></i> Create New Support Request</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="subject">Subject:</label>
            <input
              type="text"
              id="subject"
              name="subject"
              className="form-control"
              placeholder="Brief description of the issue"
              value={formData.subject}
              onChange={handleInputChange}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="body">Body:</label>
            <textarea
              id="body"
              name="body"
              className="form-control"
              rows="6"
              placeholder="Detailed description of the issue..."
              value={formData.body}
              onChange={handleInputChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="language">Language:</label>
            <select
              id="language"
              name="language"
              className="form-control"
              value={formData.language}
              onChange={handleInputChange}
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="pt">Portuguese</option>
              <option value="fr">French</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary">
            <i className="fas fa-paper-plane"></i> Submit Request
          </button>
        </form>
      </div>

      {result && (
        <div className="card">
          <h2><i className="fas fa-chart-line"></i> AI Classification Result</h2>
          <div className="request-item">
            <div className="request-header">
              <span className="request-id">ID: {result.id}</span>
              <span className={`request-category ${result.category?.toLowerCase() || 'general'}`}>
                {result.category || 'Unknown'}
              </span>
            </div>
            <div className="request-content">
              <div className="request-text">{result.text}</div>
              <div className="request-meta">
                <span>Created: {new Date(result.created_at).toLocaleString()}</span>
                <span>Language: {result.language || 'en'}</span>
              </div>
            </div>
          </div>
          
          <div className="ai-result">
            <h4><i className="fas fa-brain"></i> AI Classification</h4>
            {result.priority && <p><strong>Priority:</strong> {result.priority}</p>}
            <p><strong>Category:</strong> {result.category}</p>
            <p><strong>Confidence:</strong> {(result.confidence_score * 100).toFixed(1)}%</p>
            <div className="confidence_score-bar">
              <div 
                className="confidence_score-fill" 
                style={{ width: `${result.confidence_score * 100}%` }}
              ></div>
            </div>
            {result.summary && <p><strong>Summary:</strong> {result.summary}</p>}
          </div>
        </div>
      )}
    </>
  )
}

CreateRequest.propTypes = {
  showLoading: PropTypes.func.isRequired,
  hideLoading: PropTypes.func.isRequired
}

export default CreateRequest 
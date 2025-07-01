import PropTypes from 'prop-types'

const Header = ({ apiStatus }) => {
  return (
    <header className="header">
      <h1>
        <i className="fas fa-robot"></i> Customer Support AI Dashboard
      </h1>
      <div className="api-status">
        <span 
          className={`status-indicator ${apiStatus.online ? 'online' : 'offline'}`}
        ></span>
        <span>{apiStatus.text}</span>
      </div>
    </header>
  )
}

Header.propTypes = {
  apiStatus: PropTypes.shape({
    online: PropTypes.bool.isRequired,
    text: PropTypes.string.isRequired
  }).isRequired
}

export default Header 
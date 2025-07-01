import PropTypes from 'prop-types'

const LoadingModal = ({ show, message }) => {
  if (!show) return null

  return (
    <div className="modal show">
      <div className="modal-content">
        <div className="spinner"></div>
        <p>{message}</p>
      </div>
    </div>
  )
}

LoadingModal.propTypes = {
  show: PropTypes.bool.isRequired,
  message: PropTypes.string.isRequired
}

export default LoadingModal 
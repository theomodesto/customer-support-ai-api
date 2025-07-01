export const showError = (message) => {
  // Create a simple error notification
  const errorDiv = document.createElement('div')
  errorDiv.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #f56565;
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    z-index: 1001;
    max-width: 300px;
  `
  errorDiv.textContent = message
  
  document.body.appendChild(errorDiv)
  
  setTimeout(() => {
    errorDiv.remove()
  }, 5000)
} 
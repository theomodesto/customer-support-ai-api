import { useState, useEffect } from 'react'
import './App.css'
import Header from './components/Header'
import TabNavigation from './components/TabNavigation'
import CreateRequest from './components/CreateRequest'
import ViewRequests from './components/ViewRequests'
import Statistics from './components/Statistics'
import LoadingModal from './components/LoadingModal'
import { checkApiStatus } from './utils/api'

function App() {
  const [activeTab, setActiveTab] = useState('create')
  const [apiStatus, setApiStatus] = useState({ online: false, text: 'Checking API...' })
  const [loading, setLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('Loading...')

  useEffect(() => {
    checkApiStatus().then(setApiStatus)
    
    // Check API status every 30 seconds
    const interval = setInterval(() => {
      checkApiStatus().then(setApiStatus)
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  const showLoading = (message = 'Loading...') => {
    setLoadingMessage(message)
    setLoading(true)
  }

  const hideLoading = () => {
    setLoading(false)
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'create':
        return <CreateRequest showLoading={showLoading} hideLoading={hideLoading} />
      case 'list':
        return <ViewRequests showLoading={showLoading} hideLoading={hideLoading} />
      case 'stats':
        return <Statistics showLoading={showLoading} hideLoading={hideLoading} />
      default:
        return <CreateRequest showLoading={showLoading} hideLoading={hideLoading} />
    }
  }

  return (
    <div className="container">
      <Header apiStatus={apiStatus} />
      <TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />
      {renderTabContent()}
      <LoadingModal show={loading} message={loadingMessage} />
    </div>
  )
}

export default App

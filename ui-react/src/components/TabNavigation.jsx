import PropTypes from 'prop-types'

const TabNavigation = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'create', label: 'Create Request', icon: 'fas fa-plus-circle' },
    { id: 'list', label: 'View Requests', icon: 'fas fa-list' },
    { id: 'stats', label: 'Statistics', icon: 'fas fa-chart-bar' }
  ]

  return (
    <nav className="nav-tabs">
      {tabs.map(tab => (
        <button
          key={tab.id}
          className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => setActiveTab(tab.id)}
        >
          <i className={tab.icon}></i> {tab.label}
        </button>
      ))}
    </nav>
  )
}

TabNavigation.propTypes = {
  activeTab: PropTypes.string.isRequired,
  setActiveTab: PropTypes.func.isRequired
}

export default TabNavigation 
# Customer Support AI Dashboard - React Version

This is a React/Vite version of the Customer Support AI Dashboard, converted from the original vanilla HTML/CSS/JavaScript implementation.

## Features

- **Create Support Requests**: Submit customer messages for AI classification
- **View Requests**: Browse and filter support tickets with pagination
- **Statistics Dashboard**: View analytics and metrics
- **Real-time API Status**: Monitor backend connectivity
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and development server
- **CSS3**: Modern styling with gradients and animations
- **Font Awesome**: Icons
- **PropTypes**: Type checking for component props

## Project Structure

```
src/
├── components/
│   ├── Header.jsx              # Header with API status
│   ├── TabNavigation.jsx       # Tab navigation component
│   ├── CreateRequest.jsx       # Form for creating requests
│   ├── ViewRequests.jsx        # List and filter requests
│   ├── Statistics.jsx          # Statistics dashboard
│   └── LoadingModal.jsx        # Loading overlay
├── utils/
│   ├── api.js                  # API utility functions
│   └── notifications.js        # Error notification system
├── App.jsx                     # Main application component
├── App.css                     # Global styles
└── main.jsx                    # Application entry point
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## API Endpoints

The application expects the following API endpoints:

- `GET /health` - Health check
- `POST /requests` - Create support request
- `GET /requests` - List support requests (with pagination and filters)
- `GET /stats` - Get statistics

## Key Differences from Original

### Architecture
- **Component-based**: Modular React components instead of monolithic JavaScript
- **State Management**: React hooks for local state management
- **Props**: Component communication through props instead of global variables

### Code Organization
- **Separation of Concerns**: API calls, components, and utilities are separated
- **Reusable Components**: Components can be easily reused and tested
- **Type Safety**: PropTypes for runtime type checking

### Development Experience
- **Hot Reload**: Vite provides fast development with hot module replacement
- **Build Optimization**: Vite optimizes the build for production
- **Modern Tooling**: Uses modern JavaScript features and tooling

## Component Details

### App.jsx
Main application component that manages:
- Active tab state
- API status monitoring
- Loading state management
- Component rendering based on active tab

### Header.jsx
Displays the application title and real-time API status indicator.

### TabNavigation.jsx
Handles tab switching between Create Request, View Requests, and Statistics.

### CreateRequest.jsx
Form component for creating new support requests with:
- Input type selection (text vs structured)
- Form validation
- API integration
- Result display

### ViewRequests.jsx
List component for viewing support requests with:
- Pagination
- Category and priority filtering
- Request details display
- AI classification results

### Statistics.jsx
Dashboard component showing:
- Total requests count
- Category breakdown
- Priority distribution
- Average confidence scores

### LoadingModal.jsx
Overlay component for displaying loading states during API calls.

## Styling

The application uses modern CSS features:
- CSS Grid and Flexbox for layouts
- CSS custom properties for theming
- Backdrop filters for glassmorphism effects
- Smooth transitions and animations
- Responsive design with mobile-first approach

## Error Handling

- API errors are displayed as toast notifications
- Loading states prevent multiple simultaneous requests
- Graceful degradation when API is unavailable

## Browser Support

- Modern browsers with ES2020+ support
- Mobile browsers (iOS Safari, Chrome Mobile)
- Desktop browsers (Chrome, Firefox, Safari, Edge)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Customer Support AI API project.

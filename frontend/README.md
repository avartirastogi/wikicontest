# WikiContest Frontend - Vue.js Application

This is the Vue.js frontend for the WikiContest platform. It provides a modern, responsive user interface for managing contests, submissions, and user accounts.

## Technology Stack

- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router** - Official router for Vue.js
- **Vite** - Next-generation frontend build tool
- **Axios** - HTTP client for API requests
- **Bootstrap 5** - CSS framework for styling

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable Vue components
│   │   └── AlertContainer.vue
│   ├── views/           # Page components
│   │   ├── Home.vue
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   ├── Contests.vue
│   │   ├── Dashboard.vue
│   │   └── Profile.vue
│   ├── router/          # Vue Router configuration
│   │   └── index.js
│   ├── services/        # API service layer
│   │   └── api.js
│   ├── store/           # State management
│   │   └── index.js
│   ├── utils/           # Utility functions
│   │   └── alerts.js
│   ├── App.vue          # Root component
│   ├── main.js          # Application entry point
│   └── style.css        # Global styles
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite configuration
└── README.md            # This file
```

## Development Setup

### Prerequisites

- Node.js 16+ and npm

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

   The development server will start at `http://localhost:5173`

3. **Build for production:**
   ```bash
   npm run build
   ```

   This creates a `dist/` directory with optimized production files.

## Development Workflow

### Running the Application

1. **Start Flask backend** (in `backend/` directory):
   ```bash
   python app.py
   ```

2. **Start Vue.js frontend** (in `frontend/` directory):
   ```bash
   npm run dev
   ```

3. **Access the application:**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:5000/api`

### Building for Production

1. **Build Vue.js application:**
   ```bash
   cd frontend
   npm run build
   ```

2. **The Flask backend will automatically serve the built files** from `frontend/dist/` directory.

3. **For Toolforge deployment**, the built files are included in the deployment.

## Features

### Authentication
- User login with email/password
- User registration
- Wikimedia OAuth login
- JWT-based session management
- Protected routes

### Contest Management
- View contests (current, upcoming, past)
- Create new contests
- View contest details
- Submit articles to contests

### Dashboard
- User statistics (total score, created contests, jury memberships)
- Recent submissions
- Contest-wise scores
- Created contests list

### UI Components
- Responsive design with Bootstrap 5
- Alert notifications
- Modal dialogs
- Loading states
- Error handling

## API Integration

The frontend communicates with the Flask backend through the API service (`src/services/api.js`). All API requests:

- Include CSRF tokens for security
- Handle cookies for JWT authentication
- Provide consistent error handling
- Support request/response interceptors

## State Management

The application uses Vue 3 Composition API with a composable store pattern (`src/store/index.js`) for state management. The store manages:

- User authentication state
- Contest data
- Loading states
- UI state

## Routing

Vue Router handles client-side routing with:

- Route protection (authentication required)
- Automatic redirects
- Query parameter support
- History mode for clean URLs

## Styling

- **Bootstrap 5** for base components and layout
- **Custom CSS** for brand colors and specific styling
- **Responsive design** for mobile and desktop

## Deployment

### Local Production Build

1. Build the frontend:
   ```bash
   npm run build
   ```

2. Flask will serve files from `frontend/dist/`

### Toolforge Deployment

The built Vue.js application is deployed alongside the Flask backend. See `docs/TOOLFORGE_DEPLOYMENT.md` for details.

## Troubleshooting

### Development Server Issues

- **Port already in use**: Change the port in `vite.config.js`
- **API requests failing**: Ensure Flask backend is running on port 5000
- **CORS errors**: Check Flask CORS configuration

### Build Issues

- **Module not found**: Run `npm install` to install dependencies
- **Build errors**: Check Node.js version (requires 16+)

## Contributing

When adding new features:

1. Create components in `src/components/`
2. Create views in `src/views/`
3. Add routes in `src/router/index.js`
4. Update store if needed in `src/store/index.js`
5. Test thoroughly before committing

## License

Part of the WikiContest platform project.


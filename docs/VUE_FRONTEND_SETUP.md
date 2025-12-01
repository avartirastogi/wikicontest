# Vue.js Frontend Setup Guide

This guide explains how to set up and work with the Vue.js frontend for WikiContest.

## Overview

The WikiContest frontend has been migrated from vanilla JavaScript to **Vue.js 3** for better:
- Component-based architecture
- State management
- Developer experience
- Toolforge deployment compatibility

## Technology Stack

- **Vue.js 3** - Modern JavaScript framework
- **Vue Router** - Client-side routing
- **Vite** - Fast build tool
- **Axios** - HTTP client for API requests
- **Bootstrap 5** - CSS framework

## Prerequisites

- Node.js 16+ and npm
- Flask backend running (for API)

## Development Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The development server will start at `http://localhost:5173` with hot module replacement.

### 3. Development Workflow

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

The Vite dev server automatically proxies API requests to the Flask backend.

## Building for Production

### Build Command

```bash
cd frontend
npm run build
```

This creates a `dist/` directory with:
- Optimized JavaScript bundles
- Minified CSS
- Production-ready HTML

### Flask Integration

The Flask backend automatically detects and serves the built Vue.js files:

- **Development**: Serves from `frontend/` directory
- **Production**: Serves from `frontend/dist/` directory (if exists)

No additional configuration needed!

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
│   ├── store/           # State management (composable)
│   │   └── index.js
│   ├── utils/           # Utility functions
│   │   └── alerts.js
│   ├── App.vue          # Root component
│   ├── main.js          # Application entry point
│   └── style.css        # Global styles
├── index.html           # HTML template
├── package.json         # Dependencies
├── vite.config.js      # Vite configuration
└── dist/                # Production build (generated)
```

## Key Features

### 1. Component-Based Architecture

Each page is a Vue component with:
- Template (HTML)
- Script (JavaScript logic)
- Style (CSS)

### 2. State Management

Uses Vue 3 Composition API with a composable store pattern:

```javascript
import { useStore } from '../store'

const store = useStore()
await store.login({ email, password })
```

### 3. Routing

Vue Router handles client-side navigation with:
- Route protection (authentication)
- Automatic redirects
- Query parameters

### 4. API Integration

Centralized API service (`src/services/api.js`) handles:
- CSRF token management
- Cookie handling for JWT
- Error handling
- Request/response interceptors

## Adding New Features

### Create a New Page

1. **Create view component** in `src/views/`:
   ```vue
   <template>
     <div class="container py-5">
       <h2>New Page</h2>
     </div>
   </template>
   
   <script>
   export default {
     name: 'NewPage'
   }
   </script>
   ```

2. **Add route** in `src/router/index.js`:
   ```javascript
   {
     path: '/new-page',
     name: 'NewPage',
     component: () => import('../views/NewPage.vue')
   }
   ```

### Create a Reusable Component

1. **Create component** in `src/components/`:
   ```vue
   <template>
     <div class="my-component">
       {{ message }}
     </div>
   </template>
   
   <script>
   export default {
     name: 'MyComponent',
     props: {
       message: String
     }
   }
   </script>
   ```

2. **Use in views**:
   ```vue
   <script>
   import MyComponent from '../components/MyComponent.vue'
   
   export default {
     components: {
       MyComponent
     }
   }
   </script>
   ```

## Deployment

### Local Production Build

1. Build frontend:
   ```bash
   npm run build
   ```

2. Flask automatically serves from `dist/`

### Toolforge Deployment

1. Build frontend locally:
   ```bash
   npm run build
   ```

2. Deploy `frontend/dist/` along with backend

3. Flask serves the built files automatically

See `docs/TOOLFORGE_DEPLOYMENT.md` for complete deployment instructions.

## Troubleshooting

### Development Server Issues

- **Port already in use**: Change port in `vite.config.js`
- **API requests failing**: Ensure Flask backend is running
- **CORS errors**: Check Flask CORS configuration

### Build Issues

- **Module not found**: Run `npm install`
- **Build errors**: Check Node.js version (requires 16+)
- **Type errors**: Check Vue component syntax

### Runtime Issues

- **Routes not working**: Check Vue Router configuration
- **State not updating**: Verify store usage
- **API errors**: Check network tab and Flask logs

## Migration Notes

The frontend was migrated from vanilla JavaScript to Vue.js. Key changes:

- **State management**: From global variables to composable store
- **Routing**: From manual section switching to Vue Router
- **Components**: From DOM manipulation to Vue components
- **API calls**: From fetch to Axios with interceptors

All existing functionality has been preserved and enhanced with Vue.js features.

## Resources

- [Vue.js Documentation](https://vuejs.org/)
- [Vue Router Documentation](https://router.vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)


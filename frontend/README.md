# Customer Care AI - Frontend

This is the React frontend for the Customer Care AI chatbot application. It provides a user-friendly interface for interacting with the Rasa-powered conversational AI backend.

## Features

- Interactive chat interface with real-time responses
- Multi-language support (English, Spanish, French, German, Turkish)
- Conversation analytics dashboard
- Authentication system
- Responsive design with dark mode support
- Accessibility enhancements

## Technology Stack

- **React**: UI library
- **i18next**: Internationalization
- **Chart.js & react-chartjs-2**: Analytics visualization
- **Vite**: Build tool and development server
- **Vitest & Testing Library**: Unit testing
- **ESLint & Prettier**: Code quality and formatting

## Getting Started

### Prerequisites

- Node.js (v14+)
- npm or yarn

### Installation

1. Install dependencies:

```bash
npm install
# or
yarn install
```

2. Set up environment variables by creating a `.env` file in the frontend directory:

```
VITE_RASA_URL=http://localhost:5005
```

### Development

Start the development server:

```bash
npm run dev
# or
yarn dev
```

This will start the development server at http://localhost:5173.

### Building for Production

```bash
npm run build
# or
yarn build
```

The built files will be in the `dist` directory.

### Testing

Run tests:

```bash
npm run test
# or
yarn test
```

Run tests in watch mode:

```bash
npm run test:watch
# or
yarn test:watch
```

Generate test coverage:

```bash
npm run test:coverage
# or
yarn test:coverage
```

### Linting and Formatting

Lint the code:

```bash
npm run lint
# or
yarn lint
```

Format the code:

```bash
npm run format
# or
yarn format
```

## Project Structure

```
frontend/
├── public/           # Static assets
├── src/
│   ├── i18n/         # Internationalization files
│   │   ├── en.json   # English translations
│   │   ├── es.json   # Spanish translations
│   │   ├── fr.json   # French translations
│   │   ├── de.json   # German translations
│   │   └── tr.json   # Turkish translations
│   ├── test/         # Test setup and utilities
│   ├── App.jsx       # Main application component
│   ├── Auth.jsx      # Authentication components
│   ├── Analytics.jsx # Analytics dashboard
│   ├── Chatbot.jsx   # Main chatbot interface
│   ├── chatbot.css   # Styles for the application
│   └── main.jsx      # Entry point
├── .eslintrc.cjs     # ESLint configuration
├── .prettierrc.json  # Prettier configuration
├── index.html        # HTML template
├── package.json      # Dependencies and scripts
└── vite.config.js    # Vite configuration
```

## Component Overview

### Chatbot.jsx

The main chatbot interface component handles:
- User message input and submission
- Bot responses display
- Language switching
- Authentication integration
- Analytics toggle

### Auth.jsx

Authentication component with:
- Login form
- Registration form
- Form validation
- LocalStorage token management

### Analytics.jsx

Analytics dashboard featuring:
- Message statistics
- User vs Bot message distribution
- Intent distribution visualization
- Response time metrics

## Internationalization

The application supports multiple languages through i18next. Translations are stored in JSON files in the `src/i18n` directory.

To add a new language:
1. Create a new JSON file in the i18n directory (e.g., `it.json` for Italian)
2. Copy the structure from another language file and translate the values
3. Add the language to the language switcher in `Chatbot.jsx`

## Accessibility

The frontend includes several accessibility enhancements:
- Proper ARIA attributes
- Keyboard navigation support
- Focus management
- Screen reader friendly elements
- Color contrast compliance
- Dark mode support

## Contributing

Please ensure all code follows the ESLint and Prettier configurations. Write tests for new features and ensure all tests pass before submitting changes.

module.exports = {
  root: true,
  extends: ['react-app'],
  rules: {
    // Add any custom rules here
  },
  settings: {
    react: {
      version: 'detect'
    }
  },
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true
    }
  }
}; 
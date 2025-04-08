const { defineConfig } = require("cypress");

module.exports = defineConfig({
  projectId: 'p3766m',
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    baseUrl: 'http://localhost:5000', // Flask app URL
    supportFile: 'cypress/support/e2e.js', // Path to the support file
    specPattern: 'cypress/e2e/**/*.spec.js', // The location of your test files
  },
});

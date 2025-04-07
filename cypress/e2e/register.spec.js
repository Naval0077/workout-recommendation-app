describe('Register Flow', () => {
  // Before each test, ensure the database is clean by calling the reset DB route
  before(() => {
    // You may need to call your Flask route to reset the database before tests
    cy.request('GET', 'http://127.0.0.1:5000/reset_db'); // Ensure this route is implemented
  });

  it('should successfully register a new user with matching passwords', () => {
    cy.visit('/register');
    cy.get('input[name=email]').type('newuser@example.com');
    cy.get('input[name=password]').type('password123');
    cy.get('input[name=confirm_password]').type('password123');
    cy.get('input[type=submit]').click();

    cy.url().should('include', '/input');  // Adjust '/input' if necessary based on your app's behavior
  });

  it('should show error if passwords do not match', () => {
    cy.visit('/register');
    cy.get('input[name=email]').type('anotheruser@example.com');
    cy.get('input[name=password]').type('password123');
    cy.get('input[name=confirm_password]').type('differentpassword');
    cy.get('input[type=submit]').click();

    // Check if the error message for password mismatch is visible
    cy.url().should('include', '/register');
  });
});

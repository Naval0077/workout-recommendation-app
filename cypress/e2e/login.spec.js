describe('Login Flow', () => {
  const testUser = {
    email: 'testuser@example.com',
    password: 'test123'
  };

  before(() => {
    // Register the user first
    cy.request('GET', 'http://localhost:5000/reset_db');
    cy.register(testUser.email, testUser.password)
  });

  it('logs in with valid credentials', () => {
    cy.visit('/');
    cy.get('input[name="email"]').type(testUser.email);
    cy.get('input[name="password"]').type(testUser.password);
    cy.get('input[name="submit"]').click();

    // Or check redirected URL:
    cy.url().should('include', '/input'); // or whatever your post-login route is
  });

  it('fails to login with invalid credentials', () => {
    cy.visit('/');
    cy.get('input[name="email"]').type(testUser.email);
    cy.get('input[name="password"]').type('wrongpassword');
    cy.get('input[type="submit"]').click();

    cy.url().should('include', '/')
  });
});

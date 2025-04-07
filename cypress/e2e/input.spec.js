describe('User Profile Input', () => {
  beforeEach(() => {
    // You can mock a login session here if necessary
    cy.request('GET', 'http://127.0.0.1:5000/reset_db');
    cy.register('test@example.com', 'password');
    cy.login('test@example.com', 'password');  // You need to create this custom login command
  });

  it('should fill in the profile data and submit the form', () => {
    // Fill in the input fields
    cy.input();

    // Verify successful submission
    cy.contains('Profile updated successfully!').should('be.visible');
    cy.url().should('include', '/customize_workout');  // Assuming the user is redirected to the schedule page
  });

  it('should show validation errors when form is submitted with missing data', () => {
    // Submit the form with missing fields
    cy.get('#submit').click();

    // Check for validation error messages (these should match your form validation logic)
    cy.url().should('include', '/input');
  });
});

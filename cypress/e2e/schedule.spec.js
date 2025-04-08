describe('Workout Schedule', () => {
  beforeEach(() => {
    cy.request('GET', 'http://localhost:5000/reset_db');
    cy.register('test@example.com', 'password');
    cy.login('test@example.com', 'password');  // Custom login command
    cy.input();
    cy.visit('/customize_workout');
  });

  it('should load the page and display all days', () => {
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    days.forEach(day => {
      cy.contains(day).should('exist');
    });
  });

  it('should expand and collapse accordions', () => {
    cy.get('.accordion-button').each(($btn, index) => {
      cy.wrap($btn).click();
      cy.wrap($btn).should('have.attr', 'aria-expanded');
    });
  });

  it('should allow selecting checkboxes for a specific day', () => {
    // Open Monday's accordion
    cy.get('#collapseMonday').then($collapse => {
      if (!$collapse.hasClass('show')) {
        cy.get('#headingMonday .accordion-button').click();
      }
    });

    // Check the first 2 muscle groups for Monday
    cy.get('input[name="monday"]').eq(0).check({ force: true }).should('be.checked');
    cy.get('input[name="monday"]').eq(1).check({ force: true }).should('be.checked');
  });

  it('should submit the form after selections', () => {
    // Open a few accordions and select checkboxes
    const days = ['monday', 'wednesday', 'friday'];

    days.forEach(day => {
      cy.get(`#heading${day.charAt(0).toUpperCase() + day.slice(1)} .accordion-button`).click();
      cy.get(`input[name="${day}"]`).eq(0).check({ force: true });
    });

    cy.get('button[type="submit"]').click();

    // Assert it redirects or responds with expected behavior
    // Example: confirmation message, redirect, or successful status
    cy.url().should('include', '/schedule'); // or adjust as needed
  });
});

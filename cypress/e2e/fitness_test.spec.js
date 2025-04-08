describe('Fitness Test', () => {
  beforeEach(() => {
    cy.request('GET', 'http://localhost:5000/reset_db').then((response) => {
      expect(response.status).to.eq(200);
      cy.wait(2000)
      cy.register('test@example.com', 'password');
      cy.login('test@example.com', 'password');
      cy.url().then(url => console.log('URL after login:', url)); // Debug URL
      cy.input();
      cy.visit('/fitness_test');
    });
  });

  it('should allow the user to submit push-up and squat scores', () => {
    cy.get('input[name="pushups"]').type('20');
    cy.get('input[name="squats"]').type('30');
    cy.get('input[name="submit"]').click();
    cy.contains('Great job! Your fitness level is now');
    cy.url().should('include', '/customize_workout');
  });
});

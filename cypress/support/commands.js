// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })


Cypress.Commands.add('login', (email, password) => {
  cy.visit('/');
  cy.contains('Email')
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="password"]').type(password);
  cy.get('input[type=submit]').click();
  cy.wait(3000)
  cy.url().then((url) => {
    console.log('CI DEBUG URL:', url);
  });
  cy.url().should('include', '/input');
});

Cypress.Commands.add('register', (email, password) => {
  cy.visit('/register');
  cy.contains('Email')
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="password"]').type(password);
  cy.get('input[name=confirm_password]').type(password);
  cy.get('input[type=submit]').click();
  cy.wait(3000);
  cy.url().then((url) => {
    console.log('CI DEBUG URL:', url);
  });
});

Cypress.Commands.add('input', () => {
  cy.document().then(doc => {
    console.log("INPUT PAGE HTML:");
    console.log(doc.documentElement.innerHTML); // Output page source to Cypress logs
  });
  cy.get('input[name="height"]').type('180');  // Height field
  cy.get('input[name="weight"]').type('75');   // Weight field
  cy.get('input[name="age"]').type('25');      // Age field
  cy.get('select[name="gender"]').select('female').should('have.value', 'female');  // Select Female from gender
  cy.get('input[name="pushups"]').type('20');  // Push-ups
  cy.get('input[name="squats"]').type('25');   // Squats
  cy.get('input[name="plank_time"]').type('60');  // Plank time in seconds
  cy.get('select[name="goal"]').select('endurance').should('have.value', 'endurance');
  cy.get('select[name="commitment"]').select('medium').should('have.value', 'medium');  // Select 'Medium' from the commitment options
  cy.get('#submit').click();
});

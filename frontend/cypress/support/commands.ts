import "@testing-library/cypress/add-commands";

Cypress.Commands.add("login", (options = {}) => {
  const defaultOptions = {
    email: Cypress.env("email"),
    password: Cypress.env("password"),
  };

  const { email, password } = {
    ...defaultOptions,
    ...options,
  };

  cy.visit("/login");

  cy.findByRole("textbox", { name: /email/i }).type(email);
  cy.findByLabelText(/password/i).type(password);
  cy.findByRole("button", { name: /login/i }).click();

  cy.url().should("not.include", "/login");
});

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

  // use longer timeout for initial page load as this can take a while
  cy.findByRole("textbox", { name: /email/i, timeout: 30000 }).type(email);
  cy.findByLabelText(/password/i).type(password);
  cy.findByRole("button", { name: /login/i }).click();

  cy.url().should("not.include", "/login");
});

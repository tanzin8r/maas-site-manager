context("404 page (authenticated user)", () => {
  beforeEach(() => {
    cy.login();
  });

  it("displays a 404 page correctly for nested routes", () => {
    cy.visit("/no-such-page", { failOnStatusCode: false });

    cy.title().should("match", /MAAS Site Manager/i);

    cy.contains(/404: Page not found/i).should("be.visible");
    cy.contains("Can't find page for: /no-such-page").should("be.visible");
  });
});

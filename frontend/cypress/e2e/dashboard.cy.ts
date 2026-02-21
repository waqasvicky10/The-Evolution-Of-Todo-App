/// <reference types="cypress" />

describe("Dashboard E2E - Phase V", () => {
  const testEmail = `dash-${Date.now()}@example.com`;
  const testPassword = "Test1234!";

  before(() => {
    cy.visit("/register");
    cy.get('input[type="email"]').type(testEmail);
    cy.get('input[type="password"]').first().type(testPassword);
    cy.get('input[type="password"]').last().type(testPassword);
    cy.get('button[type="submit"]').click();
    cy.url().should("include", "/dashboard");
  });

  beforeEach(() => {
    cy.visit("/login");
    cy.get('input[type="email"]').type(testEmail);
    cy.get('input[type="password"]').type(testPassword);
    cy.get('button[type="submit"]').click();
    cy.url().should("include", "/dashboard");
  });

  it("shows search/filter/sort controls", () => {
    cy.get('input[placeholder*="Search"]').should("exist");
    cy.get("select").should("have.length.at.least", 3);
  });

  it("creates a task from the dashboard", () => {
    cy.get("textarea").first().type("Cypress test task");
    cy.contains("Create Task").click();
    cy.contains("Cypress test task", { timeout: 10000 }).should("exist");
  });

  it("filters tasks by search", () => {
    cy.get('input[placeholder*="Search"]').type("Cypress");
    cy.contains("Cypress test task").should("exist");
  });

  it("toggles a task complete", () => {
    cy.get('input[type="checkbox"]').first().click();
    cy.get(".line-through").should("exist");
  });
});

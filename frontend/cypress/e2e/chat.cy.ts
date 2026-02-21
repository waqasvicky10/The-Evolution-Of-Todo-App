/// <reference types="cypress" />

describe("AI Chatbot E2E", () => {
  const testEmail = `test-${Date.now()}@example.com`;
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
    cy.visit("/chat");
  });

  it("loads the chat page", () => {
    cy.contains("Welcome to AI Chat").should("be.visible");
  });

  it("sends a message and receives a response", () => {
    cy.get("textarea").type("Hello, can you help me with my tasks?");
    cy.get('button[type="submit"]').click();

    cy.get("textarea").should("have.value", "");
    cy.contains("Hello, can you help me", { timeout: 10000 }).should("exist");

    // Wait for assistant response
    cy.get('[class*="animate-bounce"]', { timeout: 30000 }).should("not.exist");
  });

  it("adds a task via chat", () => {
    cy.get("textarea").type("Add a task: Buy groceries for dinner");
    cy.get('button[type="submit"]').click();

    cy.get('[class*="animate-bounce"]', { timeout: 30000 }).should("not.exist");
    // Assistant should acknowledge task creation
    cy.contains(/added|created|task/i, { timeout: 15000 }).should("exist");
  });

  it("lists tasks via chat", () => {
    cy.get("textarea").type("Show me my tasks");
    cy.get('button[type="submit"]').click();

    cy.get('[class*="animate-bounce"]', { timeout: 30000 }).should("not.exist");
    cy.contains(/task|list|here/i, { timeout: 15000 }).should("exist");
  });

  it("shows voice input button", () => {
    cy.get('button[title*="voice"]').should("exist");
  });
});

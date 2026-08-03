import { test, expect } from '@playwright/test';
import { login } from './utils';

test.describe('Members Directory', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/members');
  });

  test('should display the members list', async ({ page }) => {
    // Wait for the mock data timeout (800ms in page.tsx)
    await page.waitForTimeout(1000);

    // Check if the members header is present
    await expect(page.locator('h1', { hasText: 'Member Directory' })).toBeVisible();

    // Check that the data table has rows (meaning members were loaded)
    const tableRows = page.locator('.data-table tbody tr');
    await expect(tableRows).not.toHaveCount(0);

    // We should ensure the row is not the "Loading..." or "No members found." row if data exists
    // Given the seeded data, we expect real members
    const firstRowText = await tableRows.first().textContent();
    expect(firstRowText).not.toContain('Loading...');
  });

  test('should filter members when using the search bar', async ({ page }) => {
    await page.waitForTimeout(1000); // Wait for mock data

    const tableRows = page.locator('.data-table tbody tr');
    await expect(tableRows).not.toHaveCount(0);

    // Get the name of the first member in the table
    const firstMemberName = await tableRows.first().locator('td').first().textContent();
    if (!firstMemberName) {
      // If table is empty or something went wrong, just return
      return;
    }

    // Find the search input and type a query that doesn't match the first member (e.g., a random string)
    const searchInput = page.locator('input[placeholder="Search by name or phone..."]');
    await searchInput.fill('XYZRANDOMSTRINGXYZ');

    // The first member should no longer be visible (or the table should say 'No members found.')
    await expect(page.locator('.data-table tbody tr').first()).toHaveText(/No members found/i);

    // Clear search and search for the first member
    await searchInput.fill(firstMemberName.trim());
    await expect(page.locator('.data-table tbody tr').first().locator('td').first()).toHaveText(firstMemberName.trim());
  });
});

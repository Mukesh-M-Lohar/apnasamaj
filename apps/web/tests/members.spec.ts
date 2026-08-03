import { test, expect } from '@playwright/test';

test.describe('Members Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/members');
  });

  test('should display the members list', async ({ page }) => {
    // Wait for the mock data timeout (800ms in page.tsx)
    await page.waitForTimeout(1000);
    
    // Check if the members header is present
    await expect(page.locator('h1', { hasText: 'Member Directory' })).toBeVisible();
    
    // Check if the mock members are rendered in the table/list
    await expect(page.locator('text=Rahul Sharma')).toBeVisible();
    await expect(page.locator('text=Priya Patel')).toBeVisible();
    await expect(page.locator('text=Amit Verma')).toBeVisible();
  });

  test('should filter members when using the search bar', async ({ page }) => {
    await page.waitForTimeout(1000); // Wait for mock data
    
    // Find the search input and type a query
    const searchInput = page.locator('input[placeholder="Search by name or phone..."]');
    await searchInput.fill('Rahul');
    
    // Rahul should still be visible
    await expect(page.locator('text=Rahul Sharma')).toBeVisible();
    
    // Priya and Amit should not be visible
    await expect(page.locator('text=Priya Patel')).not.toBeVisible();
    await expect(page.locator('text=Amit Verma')).not.toBeVisible();
  });
});

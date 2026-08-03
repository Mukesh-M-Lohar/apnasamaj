import { test, expect } from '@playwright/test';

test.describe('Dashboard Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display the correct page title', async ({ page }) => {
    // The page title is currently hardcoded in Next.js layout/page or derived
    // Wait for network idle to ensure the page has loaded
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveTitle(/ApnaSamaj \| Admin Portal/);
  });

  test('should display the main KPIs', async ({ page }) => {
    // Wait for the mock data timeout (800ms in page.tsx)
    await page.waitForTimeout(1000);
    
    // Check if the 4 KPI cards are rendered by checking for their text
    await expect(page.locator('text=Total Members')).toBeVisible();
    await expect(page.locator('text=Funds Raised')).toBeVisible();
    await expect(page.locator('text=Upcoming Events')).toBeVisible();
    await expect(page.locator('text=Open Complaints')).toBeVisible();
  });
});

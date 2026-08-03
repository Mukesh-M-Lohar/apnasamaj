import { test, expect } from '@playwright/test';
import { login } from './utils';

test.describe('Navigation', () => {
  test('should navigate between Dashboard and Members pages via sidebar', async ({ page }) => {
    // Start at Dashboard via login
    await login(page);
    await page.waitForLoadState('networkidle');

    // Check if on Dashboard
    await expect(page.locator('text=Total Members')).toBeVisible();

    // Click the Members link in the sidebar
    await page.locator('nav.sidebar-nav').locator('text=Members').click();

    // Check if navigated to Members page
    await expect(page).toHaveURL(/.*\/members/);
    await expect(page.locator('h1', { hasText: 'Member Directory' })).toBeVisible();

    // Click the Dashboard link in the sidebar
    await page.locator('nav.sidebar-nav').locator('text=Dashboard').click();

    // Check if navigated back to Dashboard
    await expect(page).toHaveURL(/.*\//);
    await expect(page.locator('text=Total Members')).toBeVisible();
  });
});

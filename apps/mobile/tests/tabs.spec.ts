import { test, expect } from '@playwright/test';

test.describe('Mobile Tabs', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to root to initialize local storage
    await page.goto('/');

    // Inject mock auth token to bypass login on Web
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'mock_token');
      localStorage.setItem('tenant_id', 'mock_tenant');
    });

    // Navigate to the tabs layout directly
    await page.goto('/(tabs)');
  });

  test('should render the Home tab', async ({ page }) => {
    // Since we mocked auth, we should be on the Home tab
    // Let's check for a text that belongs to the Home tab
    await expect(page.locator('text=Home').first()).toBeVisible();

    // The bottom tab bar should have all the tabs
    await expect(page.locator('text=Directory').first()).toBeVisible();
    await expect(page.locator('text=Events').first()).toBeVisible();
    await expect(page.locator('text=Donations').first()).toBeVisible();
  });
});

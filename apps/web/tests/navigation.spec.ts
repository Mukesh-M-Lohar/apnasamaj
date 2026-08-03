import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should navigate between Dashboard and Members pages via sidebar', async ({ page }) => {
    // Start at Dashboard
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check if on Dashboard
    await expect(page.locator('text=Total Members')).toBeVisible();

    // Click the Members link in the sidebar
    // The sidebar usually has a link with text "Members" or an href to "/members"
    const membersLink = page.locator('a[href="/members"]');
    await membersLink.click();
    
    // Check if navigated to Members page
    await expect(page).toHaveURL(/.*\/members/);
    await expect(page.locator('h1', { hasText: 'Member Directory' })).toBeVisible();

    // Click the Dashboard link in the sidebar
    const dashboardLink = page.locator('a[href="/"]');
    await dashboardLink.first().click();
    
    // Check if navigated back to Dashboard
    await expect(page).toHaveURL(/.*\//);
    await expect(page.locator('text=Total Members')).toBeVisible();
  });
});

import { test, expect } from '@playwright/test';

test.describe('Mobile Auth Screen', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the mobile app web build
    await page.goto('/');
  });

  test('should display the login screen and handle input', async ({ page }) => {
    // Check if the title is visible
    await expect(page.locator('text=ApnaSamaj')).toBeVisible();
    await expect(page.locator('text=Connecting Communities Digitally')).toBeVisible();

    // Find the mobile number input
    const mobileInput = page.locator('input[placeholder="e.g. +91 9876543210"]');
    await expect(mobileInput).toBeVisible();

    // Type a number
    await mobileInput.fill('9999999999');
    await expect(mobileInput).toHaveValue('9999999999');

    // Check if the Send OTP button exists
    const sendOtpButton = page.locator('text=Send OTP');
    await expect(sendOtpButton).toBeVisible();
  });
});

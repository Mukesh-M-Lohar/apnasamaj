import { Page, expect } from '@playwright/test';

export async function login(page: Page) {
  await page.goto('/login');
  await page.fill('input[type="tel"]', '+919999999999');
  await page.click('button[type="submit"]');
  // Wait for the OTP input to appear
  const otpInput = page.locator('input[type="text"][placeholder="123456"]');
  await expect(otpInput).toBeVisible();

  // It is prefilled in development, but we should make sure it is not empty
  // Actually, let's just type the OTP to be absolutely safe (123456 is mock OTP or dev OTP)
  // Wait, dev OTP might be random. So let's wait until it has a value.
  await expect(otpInput).not.toHaveValue('', { timeout: 5000 });

  await page.click('button:has-text("Verify & Login")');

  // Wait for dashboard to load
  await page.waitForSelector('text=Total Members');
}
